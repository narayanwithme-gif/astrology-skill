#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from guna_milan import (
    dasa_porutham,
    guna_milan,
    nadi_score,
)


class GunaMilanTests(unittest.TestCase):
    def test_same_nak_same_sign(self):
        a = {"moon_sign": 0, "moon_deg": 10, "moon_nak": 0}
        b = {"moon_sign": 0, "moon_deg": 10, "moon_nak": 0}
        r = guna_milan(a, b)
        self.assertEqual(r["breakdown"]["Varna"], 1.0)
        self.assertEqual(r["breakdown"]["Tara"], 3.0)
        self.assertEqual(r["breakdown"]["Yoni"], 4.0)
        self.assertEqual(r["breakdown"]["Gana"], 6.0)
        self.assertEqual(r["breakdown"]["Nadi"], 0.0)
        self.assertEqual(r["breakdown"]["Bhakoot"], 7.0)
        self.assertEqual(r["total"], 28.0)

    def test_different_nadi(self):
        a = {"moon_sign": 0, "moon_deg": 10, "moon_nak": 0}
        b = {"moon_sign": 0, "moon_deg": 10, "moon_nak": 1}
        self.assertEqual(nadi_score(a["moon_nak"], b["moon_nak"]), 8.0)

    def test_total_max(self):
        a = {"moon_sign": 3, "moon_deg": 5, "moon_nak": 10}
        b = {"moon_sign": 7, "moon_deg": 20, "moon_nak": 20}
        r = guna_milan(a, b)
        self.assertTrue(0 <= r["total"] <= 36)
        self.assertTrue(0 <= r["modern_synastry_100"] <= 100)

    def test_dasa_porutham_returns_all_ten_checks_and_convention_notes(self):
        girl = {"moon_sign": 0, "moon_nak": 0}
        boy = {"moon_sign": 6, "moon_nak": 17}
        result = dasa_porutham(girl, boy)
        self.assertEqual(
            set(result["checks"]),
            {
                "Dina",
                "Gana",
                "Mahendra",
                "Stree Deergha",
                "Yoni",
                "Rasi",
                "Rasyadhipathi",
                "Vasya",
                "Rajju",
                "Vedha",
            },
        )
        self.assertEqual(result["checks"]["Dina"]["value"], 18)
        self.assertEqual(result["checks"]["Vedha"]["status"], "unfavorable")
        self.assertIn("bride-to-groom", result["convention"])
        self.assertEqual(sum(result["counts"].values()), 10)

    def test_dina_and_stree_deergha_use_girl_to_boy_direction(self):
        girl = {"moon_sign": 0, "moon_nak": 0}
        short = dasa_porutham(girl, {"moon_sign": 1, "moon_nak": 3})
        long = dasa_porutham(girl, {"moon_sign": 1, "moon_nak": 13})
        self.assertEqual(short["checks"]["Mahendra"]["status"], "favorable")
        self.assertEqual(short["checks"]["Stree Deergha"]["status"], "unfavorable")
        self.assertEqual(long["checks"]["Stree Deergha"]["status"], "favorable")

    def test_dina_uses_three_nine_star_sections(self):
        girl = {"moon_sign": 0, "moon_nak": 0}
        good = {2, 4, 6, 8, 9, *range(10, 17), *range(18, 24), 25, 26}
        for count in range(1, 28):
            result = dasa_porutham(girl, {"moon_sign": 1, "moon_nak": count - 1})
            expected = "favorable" if count in good else "unfavorable"
            self.assertEqual(result["checks"]["Dina"]["status"], expected, count)

    def test_vashya_direction_matches_source_roles(self):
        # The source says the boy's sign attracting the girl's is the stronger direction.
        result = dasa_porutham(
            {"moon_sign": 0, "moon_nak": 0},
            {"moon_sign": 4, "moon_nak": 1},
        )
        self.assertEqual(result["checks"]["Vasya"]["status"], "favorable")

    def test_gana_porutham_preserves_role_direction(self):
        deva_girl = {"moon_sign": 0, "moon_nak": 0}
        human_boy = {"moon_sign": 1, "moon_nak": 1}
        self.assertEqual(dasa_porutham(deva_girl, human_boy)["checks"]["Gana"]["status"], "partial")
        self.assertEqual(
            dasa_porutham(human_boy, deva_girl)["checks"]["Gana"]["status"], "favorable"
        )


if __name__ == "__main__":
    unittest.main()
