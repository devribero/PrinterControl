"""Testes locais do enriquecimento SNMP, sem rede corporativa ou SQLite."""

import inspect
import os
import unittest
from unittest.mock import Mock

os.environ.setdefault("PRINT_SERVER_MODE", "mock")

from app.routes import servers  # noqa: E402
from app.services.discovery import enrich_discovered_printers  # noqa: E402
from app.services.print_server import DiscoveredPrinter  # noqa: E402
from app.services.snmp import SNMPResult, TonerInfo  # noqa: E402


def printer(name: str, ip: str, driver: str = "Mono Driver") -> DiscoveredPrinter:
    return DiscoveredPrinter(name, "TESTSRV", f"PORT_{name}", ip, driver)


def result(**kwargs) -> SNMPResult:
    defaults = dict(
        status="online",
        page_count=12345,
        toners=[TonerInfo("K", 80, 1, 10000, "Black Toner")],
        uptime="1d, 2h, 3m",
        reachable=True,
        snmp_responded=True,
        status_reason="snmp_data_available",
    )
    defaults.update(kwargs)
    return SNMPResult(**defaults)


class DiscoverySnmpTests(unittest.TestCase):
    def test_ping_and_snmp_working(self):
        client = Mock()
        client.collect.return_value = result()
        rows = enrich_discovered_printers([printer("P1", "10.0.0.1")], "real", client_factory=lambda: client)
        self.assertEqual(rows[0].status, "online")
        self.assertTrue(rows[0].reachable)
        self.assertTrue(rows[0].snmp_responded)
        self.assertEqual(rows[0].page_count, 12345)
        self.assertEqual(rows[0].toners[0].color, "K")

    def test_ping_ok_snmp_silent(self):
        client = Mock()
        client.collect.return_value = result(page_count=None, toners=[], snmp_responded=False, status_reason="ping_ok_snmp_not_responding", error="SNMP sem resposta")
        row = enrich_discovered_printers([printer("P1", "10.0.0.1")], "real", client_factory=lambda: client)[0]
        self.assertTrue(row.reachable)
        self.assertFalse(row.snmp_responded)
        self.assertEqual(row.status_reason, "ping_ok_snmp_not_responding")

    def test_ping_failed_and_timeout_and_socket_error(self):
        cases = [
            result(status="offline", reachable=False, page_count=None, toners=[], snmp_responded=False, status_reason="ping_failed"),
            result(reachable=True, page_count=None, toners=[], snmp_responded=False, status_reason="snmp_timeout"),
            result(reachable=True, page_count=None, toners=[], snmp_responded=False, status_reason="snmp_socket_error"),
        ]
        for expected, fake_result in zip(("ping_failed", "snmp_timeout", "snmp_socket_error"), cases):
            client = Mock()
            client.collect.return_value = fake_result
            row = enrich_discovered_printers([printer("P1", "10.0.0.1")], "real", client_factory=lambda: client)[0]
            self.assertEqual(row.status_reason, expected)

    def test_partial_and_missing_counter_or_toner(self):
        partial = result(page_count=123, toners=[], status_reason="snmp_partial_data")
        no_counter = result(page_count=None, status_reason="snmp_without_page_count")
        for fake_result, expected in ((partial, "snmp_partial_data"), (no_counter, "snmp_without_page_count")):
            client = Mock()
            client.collect.return_value = fake_result
            row = enrich_discovered_printers([printer("P1", "10.0.0.1")], "real", client_factory=lambda: client)[0]
            self.assertEqual(row.status_reason, expected)

    def test_mono_and_color_toners(self):
        client = Mock()
        client.collect.side_effect = [
            result(toners=[TonerInfo("K", 80, 1)]),
            result(toners=[TonerInfo("C", 70, 2), TonerInfo("M", 60, 3), TonerInfo("Y", 50, 4), TonerInfo("K", 40, 1)]),
        ]
        rows = enrich_discovered_printers(
            [printer("Mono", "10.0.0.1"), printer("Color", "10.0.0.2", "M6530 Color")],
            "real",
            client_factory=lambda: client,
        )
        self.assertEqual([t.color for t in rows[0].toners], ["K"])
        self.assertEqual([t.color for t in rows[1].toners], ["C", "M", "Y", "K"])

    def test_label_without_printer_mib_does_not_collect_snmp(self):
        client = Mock()
        client._ping.return_value = True
        row = enrich_discovered_printers([printer("Etiqueta", "10.0.0.1", "Elgin TT042")], "real", client_factory=lambda: client)[0]
        self.assertTrue(row.reachable)
        self.assertFalse(row.snmp_responded)
        self.assertEqual(row.status_reason, "snmp_not_applicable")
        client.collect.assert_not_called()

    def test_invalid_ip_does_not_touch_network(self):
        client = Mock()
        row = enrich_discovered_printers([printer("USB", "USB001")], "real", client_factory=lambda: client)[0]
        self.assertIsNone(row.ip)
        self.assertFalse(row.reachable)
        self.assertEqual(row.status_reason, "invalid_or_missing_ip")
        client.collect.assert_not_called()
        client._ping.assert_not_called()

    def test_deduplicates_ip_and_preserves_queues(self):
        client = Mock()
        client.collect.return_value = result()
        rows = enrich_discovered_printers(
            [printer("A", "10.0.0.1"), printer("B", "10.0.0.1"), printer("C", "10.0.0.2")],
            "real",
            client_factory=lambda: client,
        )
        self.assertEqual([row.name for row in rows], ["A", "B", "C"])
        self.assertEqual(client.collect.call_count, 2)
        self.assertEqual(rows[0].ip_group_size, 2)
        self.assertTrue(rows[0].network_query_reused)

    def test_one_error_does_not_stop_other_ips(self):
        client = Mock()
        client.collect.side_effect = [TimeoutError(), result()]
        rows = enrich_discovered_printers(
            [printer("A", "10.0.0.1"), printer("B", "10.0.0.2")],
            "real",
            client_factory=lambda: client,
        )
        self.assertEqual(rows[0].status_reason, "snmp_timeout")
        self.assertEqual(rows[1].status, "online")

    def test_mock_mode_uses_mock_client_without_network(self):
        rows = enrich_discovered_printers([printer("P1", "10.0.0.1")], "mock")
        self.assertEqual(rows[0].status_reason, "snmp_data_available")
        self.assertTrue(rows[0].snmp_responded)

    def test_route_has_no_database_session(self):
        self.assertNotIn("session", inspect.signature(servers.discover).parameters)
        self.assertNotIn("session", inspect.getsource(servers.discover))
        source = inspect.getsource(enrich_discovered_printers)
        for forbidden in ("Session", "PrinterReading", "collect_and_save", "evaluate_reading", "sync_printers"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()