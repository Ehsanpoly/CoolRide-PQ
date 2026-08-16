import unittest

from coolride_pq.config import load_site_config
from coolride_pq.control import SupervisoryController
from coolride_pq.models import OperatingMode, Telemetry, TelemetryQuality


def telemetry(**changes: object) -> Telemetry:
    payload: dict[str, object] = {
        "timestamp": "2026-08-19T18:03:00+00:00",
        "hour": 18.05,
        "quality": TelemetryQuality.GOOD,
        "pcc_active_power_mw": 64.0,
        "pcc_reactive_power_mvar": 5.0,
        "pcc_voltage_pu": 0.89,
        "frequency_hz": 59.97,
        "thdv_percent": 5.5,
        "it_power_mw": 48.0,
        "cooling_power_mw": 14.0,
        "maximum_inlet_temperature_c": 24.0,
        "bess_soc": 0.70,
        "thermal_soc": 0.60,
        "grid_alert": True,
        "operator_enable": True,
    }
    payload.update(changes)
    return Telemetry(**payload)  # type: ignore[arg-type]


class ControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = SupervisoryController(load_site_config())

    def test_voltage_sag_prioritizes_ride_through(self) -> None:
        decision = self.controller.decide(telemetry())
        self.assertEqual(decision.mode, OperatingMode.VOLTAGE_RIDE_THROUGH)
        self.assertGreater(decision.bess_reactive_power_mvar, 0.0)
        self.assertEqual(decision.active_filter_percent, 80.0)
        self.assertTrue(decision.advisory_only)

    def test_stale_telemetry_fails_closed(self) -> None:
        decision = self.controller.decide(telemetry(quality=TelemetryQuality.STALE))
        self.assertEqual(decision.mode, OperatingMode.SAFE_HOLD)
        self.assertEqual(decision.bess_active_power_mw, 0.0)

    def test_temperature_limit_fails_closed(self) -> None:
        decision = self.controller.decide(telemetry(maximum_inlet_temperature_c=27.0))
        self.assertEqual(decision.mode, OperatingMode.SAFE_HOLD)


if __name__ == "__main__":
    unittest.main()
