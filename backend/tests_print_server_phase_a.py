"""Fase A: transporte simulado e SQLite em memoria; sem rede/banco de operacao.

Executar: venv/Scripts/python.exe tests_print_server_phase_a.py
"""
import json
import os
import subprocess
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_tmp = tempfile.TemporaryDirectory(prefix="printercontrol-phase-a-")
os.environ.update(ENVIRONMENT="development", PRINT_SERVER_MODE="mock",
                  DATABASE_URL=f"sqlite:///{Path(_tmp.name).as_posix()}/unused.db",
                  COLLECTION_ENABLED="false", LOG_DIR=_tmp.name)

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.pool import StaticPool
from app.config import Settings, settings
from app.database import get_session
from app.dependencies import require_active_user, _network_action_limiter
from app.main import app
from app.models.user import User
from app.models.printer import Printer
from app.models.print_server import PrintServer
from app.services import print_server as ps, printer_sync as sync


def completed(stdout="", stderr="", returncode=0):
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


def printer(name, server="TESTSRV"):
    return ps.DiscoveredPrinter(name, server, "IP_1", "10.0.0.1", "Driver")


class TransportTests(unittest.TestCase):
    def run_output(self, output):
        with patch.object(ps, "_effective_identity", return_value=("DOMAIN\\svc", None)), \
             patch.object(ps.subprocess, "run", return_value=output):
            return ps._run_powershell_json("Get-Printer", 3, server="TESTSRV", operation="Get-Printer")

    def test_error_categories(self):
        cases = [
            ({"stage": "dns", "native_code": 11001}, "dns_resolution_failed"),
            ({"hresult": -2147023174}, "rpc_timeout_or_unavailable"),
            ({"hresult": -2147024891}, "access_denied"),
            ({"message": "The print spooler service is not running"}, "spooler_unavailable"),
            ({"type": "System.Management.Automation.CommandNotFoundException"}, "cmdlet_not_found"),
            ({"error_id": "HRESULT 0x80070005,Get-Printer", "message": "mensagem localizada"}, "access_denied"),
            ({"native_status": "AccessDenied"}, "access_denied"),
            ({"error_id": "HRESULT 0x800706ba,Get-Printer"}, "rpc_timeout_or_unavailable"),
            ({"message": "falha ambigua"}, "unknown_error"),
        ]
        for evidence, expected in cases:
            with self.subTest(expected=expected), self.assertRaises(ps.PrintServerError) as ctx:
                self.run_output(completed(stderr="PRINT_SERVER_ERROR:" + json.dumps(evidence), returncode=1))
            self.assertEqual(ctx.exception.category, expected)
            self.assertEqual(ctx.exception.context["identity"], "DOMAIN\\svc")
            self.assertGreaterEqual(ctx.exception.context["duration_ms"], 0)

    def test_invalid_json_and_shape(self):
        for raw in ('bad json', 'true', '123', '"text"', '[null]', '{}', '[{"Name":null}]'):
            with self.subTest(raw=raw), self.assertRaises(ps.PrintServerError) as ctx:
                self.run_output(completed(raw))
            self.assertEqual(ctx.exception.category, "invalid_json")

    def test_empty_single_array_unicode(self):
        for raw, count in [('', 0), ('null', 0), ('[]', 0), ('{"Name":"Fila ação"}', 1),
                           ('[{"Name":"A"},{"Name":"B"}]', 2)]:
            with self.subTest(raw=raw):
                self.assertEqual(len(self.run_output(completed(raw))), count)

    def test_timeout_and_missing_powershell(self):
        for failure, expected in [(subprocess.TimeoutExpired("powershell.exe", 3), "rpc_timeout_or_unavailable"),
                                  (FileNotFoundError(), "powershell_not_found"),
                                  (PermissionError(), "transport_unavailable")]:
            with self.subTest(expected=expected), \
                 patch.object(ps, "_effective_identity", return_value=("DOMAIN\\svc", None)), \
                 patch.object(ps.subprocess, "run", side_effect=failure), \
                 self.assertRaises(ps.PrintServerError) as ctx:
                ps._run_powershell_json("Get-Printer", 3)
            self.assertEqual(ctx.exception.category, expected)

    def test_identity_each_command_and_counts(self):
        outputs = [completed("DOMAIN\\svc\n"), completed('[{"Name":"A","PortName":"IP_1"}]'),
                   completed("DOMAIN\\svc\n"), completed('[{"Name":"IP_1","PrinterHostAddress":"10.0.0.1"}]')]
        with patch.object(ps.subprocess, "run", side_effect=outputs) as run, \
             self.assertLogs(ps.logger, level="INFO") as logs:
            result = ps._real_discover("TESTSRV", 3)
        self.assertEqual(result[0].ip, "10.0.0.1")
        self.assertEqual([c.args[0][0] for c in run.call_args_list],
                         ["whoami.exe", "powershell.exe", "whoami.exe", "powershell.exe"])
        final = [r for r in logs.output if "resultado" in r]
        self.assertEqual(len(final), 2)
        self.assertIn("Get-PrinterPort", final[1])
        for line in final:
            self.assertIn("duration_ms", line)
            self.assertIn("'count': 1", line)
            self.assertIn("DOMAIN", line)

    def test_whoami_failure_does_not_invent_identity(self):
        with patch.object(ps.subprocess, "run", side_effect=[FileNotFoundError(), completed('[]')]), \
             patch.object(settings, "print_server_host", "TESTSRV"):
            result = ps.diagnose_print_server()
        self.assertTrue(result["success"])
        self.assertIsNone(result["identity"])
        self.assertEqual(result["identity_error"], "whoami_unavailable")

    def test_invalid_host_before_subprocess(self):
        with patch.object(ps.subprocess, "run") as run, self.assertRaises(ps.PrintServerError):
            ps._real_discover("bad';host", 3)
        run.assert_not_called()


class ConfigTests(unittest.TestCase):
    def production(self, **kwargs):
        base = dict(environment="production", secret_key="x" * 48,
                    allow_mock_collect=False, cors_origins=["https://example.com"], _env_file=None)
        base.update(kwargs)
        return Settings(**base)

    def test_mock_requires_development_or_demo(self):
        for environment in ("development", "demo"):
            self.assertEqual(Settings(environment=environment, _env_file=None).print_server_mode, "mock")
        for mode in ("mock", "", "invalid"):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                self.production(print_server_mode=mode)
        self.assertEqual(self.production(print_server_mode=" REAL ").print_server_mode, "real")

    def test_missing_mode_or_missing_env_file_cannot_mock_in_production(self):
        with patch.dict(os.environ, {}, clear=True):
            for env_file in (None, str(Path(_tmp.name) / "missing.env")):
                with self.subTest(env_file=env_file), self.assertRaisesRegex(ValueError, "PRINT_SERVER_MODE"):
                    self.production(_env_file=env_file)
            for mode in ("", "wrong"):
                with self.assertRaises(ValueError):
                    Settings(print_server_mode=mode, _env_file=None)

    def test_unknown_environment_and_timeout(self):
        for env in ("staging", "prod", ""):
            with self.assertRaises(ValueError):
                Settings(environment=env, _env_file=None)
        with self.assertRaises(ValueError):
            Settings(print_server_timeout_seconds=0, _env_file=None)

    def test_service_override_cannot_mock_in_production(self):
        with patch.object(settings, "environment", "production"), self.assertRaises(ps.PrintServerError):
            ps.discover_printers(mode="mock")


@unittest.skipUnless(shutil.which("powershell.exe"), "PowerShell Windows nao instalado")
class LocalPowerShellTests(unittest.TestCase):
    """Valida o wrapper no PowerShell instalado; nao acessa Print Server."""

    def test_local_json_and_identity(self):
        telemetry = {}
        result = ps._run_powershell_json(
            "[pscustomobject]@{Name='Fila ação'} | ConvertTo-Json -Compress", 10,
            server="localhost", operation="local-test", telemetry=telemetry,
        )
        self.assertEqual(result, [{"Name": "Fila ação"}])
        self.assertTrue(telemetry["identity"])

    def test_local_structured_errors(self):
        for command, category in [
            ("Get-PrinterControlCmdletInexistente", "cmdlet_not_found"),
            ("throw [System.UnauthorizedAccessException]::new('Teste de permissao')", "access_denied"),
            ("Write-Output 'nao JSON'", "invalid_json"),
        ]:
            with self.subTest(category=category), self.assertRaises(ps.PrintServerError) as ctx:
                ps._run_powershell_json(command, 10, operation="local-test")
            self.assertEqual(ctx.exception.category, category)


class DatabaseFixture:
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.server = PrintServer(host="TESTSRV", mode="real")
        self.session.add(self.server)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def seed(self, count=100, inactive=0):
        for i in range(count + inactive):
            self.session.add(Printer(server="TESTSRV", name=f"P{i}", model="Original", ip="10.0.0.1",
                                     active=i < count))
        self.session.add(Printer(server="OTHER", name="OTHER", model="Original", ip="10.0.0.2"))
        self.session.commit()

    def snapshot(self):
        return [p.model_dump() for p in self.session.exec(select(Printer).order_by(Printer.id)).all()]


class DatabaseTests(DatabaseFixture, unittest.TestCase):

    def test_large_drop_atomic_and_duplicates_do_not_hide_drop(self):
        self.seed()
        before = self.snapshot()
        for rows in ([printer(f"P{i}") for i in range(79)], [], [printer("P0")] * 100):
            with self.subTest(count=len(rows)), patch.object(sync, "discover_printers", return_value=rows), \
                 self.assertLogs(sync.logger, level="ERROR"), self.assertRaises(sync.SyncBlockedError) as ctx:
                sync.sync_printers(self.session, "TESTSRV")
            self.assertEqual(ctx.exception.context["registered_active"], 100)
            self.assertEqual(self.snapshot(), before)
            self.assertFalse(self.session.dirty)

    def test_exact_twenty_percent_and_historical_inactive(self):
        self.seed(100, 30)
        with patch.object(sync, "discover_printers", return_value=[printer(f"P{i}") for i in range(80)]):
            result = sync.sync_printers(self.session, "TESTSRV")
        self.assertEqual(result.deactivated, 20)
        self.assertTrue(self.session.exec(select(Printer).where(Printer.server == "OTHER")).one().active)

    def test_initial_discovery_and_zero_active(self):
        self.seed(0, 10)
        with patch.object(sync, "discover_printers", return_value=[printer("P0"), printer("new")]):
            result = sync.sync_printers(self.session, "TESTSRV")
        self.assertEqual((result.created, result.reactivated), (1, 1))

    def test_empty_initial_discovery(self):
        with patch.object(sync, "discover_printers", return_value=[]):
            self.assertEqual(sync.sync_printers(self.session, "TESTSRV").discovered, 0)

    def test_discovery_error_no_writes(self):
        self.seed()
        before = self.snapshot()
        with patch.object(sync, "discover_printers", side_effect=ps.PrintServerError("denied", "access_denied")), \
             self.assertRaises(ps.PrintServerError):
            sync.sync_printers(self.session, "TESTSRV")
        self.assertEqual(before, self.snapshot())


class ApiTests(DatabaseFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client = TestClient(app)
        app.dependency_overrides[get_session] = lambda: self.session
        self.admin = User(email="admin@test", name="Admin", password_hash="unused", role="admin")
        app.dependency_overrides[require_active_user] = lambda: self.admin
        self.host_patch = patch.object(settings, "print_server_host", "TESTSRV")
        self.host_patch.start()
        _network_action_limiter.reset()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.host_patch.stop()
        self.client.close()
        _network_action_limiter.reset()
        super().tearDown()

    def test_real_probe_even_when_mock_and_no_db_writes(self):
        self.seed()
        before = self.snapshot()
        with patch.object(ps.subprocess, "run", side_effect=[completed("DOMAIN\\svc"), completed('[{"Name":"P"}]')]) as run:
            response = self.client.get("/health/print-server")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual((data["configured_mode"], data["probe_mode"]), ("mock", "real"))
        self.assertEqual(data["identity"], "DOMAIN\\svc")
        self.assertEqual(data["count"], 1)
        self.assertEqual(before, self.snapshot())
        command = run.call_args_list[1].args[0][-1]
        self.assertIn("Get-Printer -ComputerName 'TESTSRV' -ErrorAction Stop", command)
        self.assertNotIn("Get-PrinterPort", command)

    def test_probe_failure_structured(self):
        evidence = {"hresult": -2147024891, "message": "Acesso negado"}
        with patch.object(ps.subprocess, "run", side_effect=[completed("DOMAIN\\svc"),
                completed(stderr="PRINT_SERVER_ERROR:" + json.dumps(evidence), returncode=1)]):
            response = self.client.get("/health/print-server")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["category"], "access_denied")
        self.assertEqual(response.json()["identity"], "DOMAIN\\svc")
        self.assertFalse(response.json()["success"])

    def test_probe_auth_and_rate_limit(self):
        app.dependency_overrides.pop(require_active_user)
        with patch.object(ps.subprocess, "run") as run:
            self.assertEqual(self.client.get("/health/print-server").status_code, 401)
            for role in ("viewer", "operator"):
                self.admin.role = role
                app.dependency_overrides[require_active_user] = lambda: self.admin
                self.assertEqual(self.client.get("/health/print-server").status_code, 403)
            run.assert_not_called()
        self.admin.role = "admin"
        with patch("app.routes.health.diagnose_print_server", return_value={"success": True}):
            for _ in range(settings.network_action_max_attempts):
                self.assertEqual(self.client.get("/health/print-server").status_code, 200)
            response = self.client.get("/health/print-server")
        self.assertEqual(response.status_code, 429)
        self.assertIn("retry-after", response.headers)

    def test_both_sync_routes_block_and_persist_alert_only(self):
        self.seed()
        before = self.snapshot()
        for url in ("/api/servers/sync", f"/api/servers/{self.server.id}/sync"):
            with patch.object(sync, "discover_printers", return_value=[]):
                response = self.client.post(url)
            self.assertEqual(response.status_code, 409)
            self.assertEqual(response.json()["category"], "sync_discovery_drop_blocked")
            self.assertEqual(response.json()["registered_active"], 100)
            self.assertIsInstance(response.json()["detail"], str)
            self.assertEqual(self.snapshot(), before)
            self.session.refresh(self.server)
            self.assertIn("sync_discovery_drop_blocked", self.server.last_error)
            self.assertIsNone(self.server.last_sync_at)

        # Recuperacao do caminho padrao tambem precisa limpar o alerta antigo.
        with patch.object(sync, "discover_printers", return_value=[printer(f"P{i}") for i in range(100)]):
            response = self.client.post("/api/servers/sync")
        self.assertEqual(response.status_code, 200)
        self.session.refresh(self.server)
        self.assertIsNone(self.server.last_error)
        self.assertEqual(self.server.last_status, "online")
        self.assertIsNotNone(self.server.last_sync_at)

    def test_discovery_api_error_preserves_detail(self):
        with patch("app.routes.servers.discover_printers", side_effect=ps.PrintServerError("denied", "access_denied")):
            response = self.client.post("/api/servers/discover")
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "denied")
        self.assertEqual(response.json()["category"], "access_denied")


if __name__ == "__main__":
    unittest.main(verbosity=2)
