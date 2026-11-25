import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


@unittest.skipUnless(importlib.util.find_spec("jhora"), "install optional [vedic-full] extra")
class FullVedicExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import vedic_extensions

        cls.extension = vedic_extensions

    def test_upstream_dasha_catalog_exposes_only_wired_selectors(self):
        catalog = self.extension.dasha_catalog()
        self.assertGreaterEqual(catalog["count"], 50)
        self.assertTrue(all(row["selector_wired"] for row in catalog["systems"]))
        self.assertIn("does not claim", catalog["scope_note"])

    def test_source_language_catalog_has_22_codes(self):
        languages = self.extension.language_catalog()
        self.assertEqual(len(languages), 22)
        self.assertIn("hi", {row["code"] for row in languages})

    def test_festival_matches_include_source_and_translation_fallback(self):
        result = self.extension.festival_calendar(
            "2026-11-01", "2026-11-01", "Asia/Kolkata", 19.076, 72.878, "or", "Mumbai"
        )
        self.assertEqual(result["dates"][0]["date"], "2026-11-01")
        self.assertTrue(result["dates"][0]["festivals"])
        self.assertTrue(
            all(row["name"] == row["name_en"] for row in result["dates"][0]["festivals"])
        )
        self.assertTrue(all(row["calendar_type"] != "4" for row in result["dates"][0]["festivals"]))
        self.assertIn("PyJHora", result["source"])
        self.assertIn("sampradaya", result["convention_note"])

    def test_named_vrata_rule_returns_dates_and_convention_note(self):
        result = self.extension.vrata_dates(
            "2026-11-01",
            "2026-11-30",
            "ekadhashi",
            "Asia/Kolkata",
            19.076,
            72.878,
            "Mumbai",
        )
        self.assertTrue(result["dates"])
        self.assertIn("PyJHora", result["source"])
        self.assertIn("regional calendar", result["convention_note"])

    def test_single_day_vrata_search_includes_boundary_dates_and_local_times(self):
        result = self.extension.vrata_dates(
            "2026-11-05",
            "2026-11-05",
            "ekadhashi",
            "Asia/Kolkata",
            19.076,
            72.878,
            "Mumbai",
        )
        self.assertEqual([row["date"] for row in result["dates"]], ["2026-11-05"])
        self.assertIn("T", result["dates"][0]["start_local"])

    def test_invalid_language_and_date_range_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported language"):
            self.extension.festival_calendar(
                "2026-11-01", "2026-11-02", "Asia/Kolkata", 19.076, 72.878, "xx"
            )
        with self.assertRaisesRegex(ValueError, "Unsupported calendar"):
            self.extension.festival_calendar(
                "2026-11-01",
                "2026-11-02",
                "Asia/Kolkata",
                19.076,
                72.878,
                calendar="xx",
            )
        with self.assertRaisesRegex(ValueError, "on or after"):
            self.extension.vrata_dates(
                "2026-11-02", "2026-11-01", "ekadhashi", "Asia/Kolkata", 19, 72
            )


if __name__ == "__main__":
    unittest.main()
