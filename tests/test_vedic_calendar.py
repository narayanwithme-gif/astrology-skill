import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import vedic_calendar


class VedicCalendarTests(unittest.TestCase):
    def test_sunrise_calendar_returns_limbs_and_local_boundary(self):
        result = vedic_calendar.panchanga_at_sunrise(
            date(2024, 1, 1), "Asia/Kolkata", 28.6139, 77.209
        )
        self.assertEqual(result["date"], "2024-01-01")
        self.assertEqual(result["day_boundary"], "sunrise")
        self.assertEqual(result["timezone"], "Asia/Kolkata")
        self.assertIn(result["tithi"]["number"], range(1, 31))
        self.assertIn(result["nakshatra"]["number"], range(1, 28))
        self.assertIn(result["yoga"]["number"], range(1, 28))
        self.assertIn(result["karana"]["number"], range(1, 61))
        self.assertIn(result["sunrise_local"][11:13], {"05", "06", "07"})

    def test_calendar_month_has_day_count_and_explicit_limits(self):
        result = vedic_calendar.month_calendar(2024, 2, "Asia/Kolkata", 28.6, 77.2)
        self.assertEqual(len(result["days"]), 29)
        self.assertEqual(result["leading_blank_days"], 3)
        self.assertIn("not a regional festival", result["scope_note"])

    def test_invalid_month_rejected(self):
        with self.assertRaisesRegex(ValueError, "month"):
            vedic_calendar.month_calendar(2024, 13, "Asia/Kolkata", 0, 0)


if __name__ == "__main__":
    unittest.main()
