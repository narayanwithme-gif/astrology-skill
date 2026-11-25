import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from vedic_predictions import interpret_chart, rule_catalog


class VedicPredictionTests(unittest.TestCase):
    def test_rule_library_contains_108_plus_rule_templates(self):
        catalog = rule_catalog()
        self.assertEqual(len(catalog["graha_bhava_rules"]), 108)
        self.assertEqual(len(catalog["bhava_lord_rules"]), 144)
        self.assertEqual(catalog["count"], 252)
        ids = [
            rule["id"]
            for rules in (catalog["graha_bhava_rules"], catalog["bhava_lord_rules"])
            for rule in rules
        ]
        self.assertEqual(len(ids), len(set(ids)))

    def test_chart_interpretation_emits_evidence_backed_placements(self):
        planets = {
            name: {"house": (index % 12) + 1, "sign": "Aries"}
            for index, name in enumerate(
                ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
            )
        }
        result = interpret_chart({"ascendant": {"sign_index": 0}, "planets": planets})
        self.assertEqual(result["rule_library_size"], 252)
        self.assertEqual(len(result["graha_in_bhava"]), 9)
        self.assertEqual(len(result["bhava_lord_in_bhava"]), 12)
        self.assertEqual(result["count_for_chart"], 21)
        self.assertIn("not an outcome", result["bhava_lord_in_bhava"][0]["reading_prompt"])


if __name__ == "__main__":
    unittest.main()
