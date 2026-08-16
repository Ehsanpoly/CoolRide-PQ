import unittest

from coolride_pq.config import load_site_config
from coolride_pq.sizing import size_site


class SizingTests(unittest.TestCase):
    def test_reference_site(self) -> None:
        result = size_site(load_site_config())
        self.assertEqual(result.facility_capacity_mw, 65.0)
        self.assertEqual(result.rack_count, 625)
        self.assertEqual(result.installed_ups_modules, 12)
        self.assertEqual(result.bess_duration_hours_at_rated_power, 3.0)


if __name__ == "__main__":
    unittest.main()
