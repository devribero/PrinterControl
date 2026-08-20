"""Testes isolados da descoberta do Print Server, sem rede ou banco real."""

import inspect
import json
import os
import subprocess
import unittest
from unittest.mock import patch

os.environ.setdefault("PRINT_SERVER_MODE", "mock")

from app.config import settings  # noqa: E402
from app.routes import servers  # noqa: E402
from app.services import print_server  # noqa: E402
from app.services.print_server import DiscoveredPrinter, PrintServerError  # noqa: E402


class PrintServerDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.previous_mode = settings.print_server_mode
        self.previous_host = settings.print_server_host
        settings.print_server_host = "TESTSRV"

    def tearDown(self):
        settings.print_server_mode = self.previous_mode
        settings.print_server_host = self.previous_host

    def test_mock_declares_source_and_unresolved_port(self):
        settings.print_server_mode = "mock"

        result = servers.discover(object())

        self.assertEqual(result.source, "print_server_mock")
        usb = next(item for item in result.printers if item.port_name == "USB001")
        self.assertIsNone(usb.ip)
        self.assertEqual(usb.ip_resolution, "unresolved")

    def test_real_uses_fake_powershell_output(self):
        settings.print_server_mode = "real"
        commands = [
            [{"Name": "Fila 1", "DriverName": "Driver X", "PortName": "IP_1"}],
            [{"Name": "IP_1", "PrinterHostAddress": "10.0.0.5"}],
        ]

        with patch.object(print_server, "_run_powershell_json", side_effect=commands) as run:
            result = print_server.discover_printers()

        self.assertEqual(result, [DiscoveredPrinter("Fila 1", "TESTSRV", "IP_1", "10.0.0.5", "Driver X")])
        self.assertEqual(run.call_count, 2)

    def test_empty_print_server_response(self):
        settings.print_server_mode = "real"
        with patch.object(print_server, "_run_powershell_json", side_effect=[[], []]):
            result = print_server.discover_printers()
        self.assertEqual(result, [])

    def test_powershell_error_and_timeout_are_explicit(self):
        with patch("app.services.print_server.subprocess.run", side_effect=subprocess.TimeoutExpired("powershell.exe", 30)):
            with self.assertRaisesRegex(PrintServerError, "nao respondeu"):
                print_server._run_powershell_json("Get-Printer", 30)

        failed = subprocess.CompletedProcess(
            args=["powershell.exe"], returncode=1, stdout="", stderr="falha controlada"
        )
        with patch("app.services.print_server.subprocess.run", return_value=failed):
            with self.assertRaisesRegex(PrintServerError, "PowerShell falhou"):
                print_server._run_powershell_json("Get-Printer", 30)

    def test_ip_absent_is_not_presented_as_network_ip(self):
        item = servers.DiscoveredPrinterResponse(
            name="Fila",
            server="TESTSRV",
            port_name="USB001",
            ip=None,
            driver_name="Driver",
            source="print_server_real",
            ip_resolution="unresolved",
        )
        self.assertIsNone(item.ip)
        self.assertEqual(item.ip_resolution, "unresolved")

    def test_discovery_route_does_not_depend_on_database_session(self):
        self.assertNotIn("session", inspect.signature(servers.discover).parameters)
        self.assertNotIn("session", inspect.getsource(servers.discover))


if __name__ == "__main__":
    unittest.main()