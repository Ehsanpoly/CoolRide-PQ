import unittest

from coolride_pq.config import load_site_config
from coolride_pq.evidence import build_evidence_bundle
from coolride_pq.simulation import simulate_reference_day


class SimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_site_config()
        cls.scenario = simulate_reference_day(cls.config)

    def test_deterministic_shape(self) -> None:
        self.assertEqual(len(self.scenario["rows"]), 289)
        self.assertEqual(self.scenario["time_step_minutes"], 5)

    def test_default_scenario_improves_target_metrics(self) -> None:
        metrics = self.scenario["metrics"]
        self.assertGreater(metrics["net_energy_change_mwh"], 0.0)
        self.assertGreater(metrics["peak_reduction_mw"], 0.0)
        self.assertGreater(
            metrics["minimum_voltage_controlled_pu"],
            metrics["minimum_voltage_baseline_pu"],
        )
        self.assertLess(
            metrics["maximum_thdv_controlled_percent"],
            metrics["maximum_thdv_baseline_percent"],
        )
        self.assertLess(metrics["maximum_inlet_temperature_c"], 27.0)

    def test_storage_day_is_not_free_energy(self) -> None:
        metrics = self.scenario["metrics"]
        self.assertGreaterEqual(metrics["ending_bess_soc"], 0.44)
        self.assertGreaterEqual(metrics["ending_thermal_soc"], 0.29)

    def test_evidence_is_hashed_and_labeled(self) -> None:
        evidence = build_evidence_bundle(self.config, self.scenario)
        self.assertEqual(evidence["classification"], "synthetic-engineering-reference")
        self.assertEqual(len(evidence["scenario_sha256"]), 64)
        self.assertEqual(evidence["sample_count"], 289)


if __name__ == "__main__":
    unittest.main()
