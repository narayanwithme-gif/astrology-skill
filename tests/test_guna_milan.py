#!/usr/bin/env python3
import unittest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from guna_milan import guna_milan, varna_score, gana_score, nadi_score, bhakoot_score

class GunaMilanTests(unittest.TestCase):
    def test_same_nak_same_sign(self):
        a={"moon_sign":0,"moon_deg":10,"moon_nak":0}; b={"moon_sign":0,"moon_deg":10,"moon_nak":0}
        r=guna_milan(a,b)
        self.assertEqual(r["breakdown"]["Varna"],1.0)
        self.assertEqual(r["breakdown"]["Tara"],3.0)
        self.assertEqual(r["breakdown"]["Yoni"],4.0)
        self.assertEqual(r["breakdown"]["Gana"],6.0)
        self.assertEqual(r["breakdown"]["Nadi"],0.0)
        self.assertEqual(r["breakdown"]["Bhakoot"],7.0)
        self.assertEqual(r["total"],28.0)

    def test_different_nadi(self):
        a={"moon_sign":0,"moon_deg":10,"moon_nak":0}; b={"moon_sign":0,"moon_deg":10,"moon_nak":1}
        self.assertEqual(nadi_score(a["moon_nak"],b["moon_nak"]),8.0)

    def test_total_max(self):
        a={"moon_sign":3,"moon_deg":5,"moon_nak":10}; b={"moon_sign":7,"moon_deg":20,"moon_nak":20}
        r=guna_milan(a,b)
        self.assertTrue(0<=r["total"]<=36)
        self.assertTrue(0<=r["modern_synastry_100"]<=100)

if __name__=="__main__":
    unittest.main()
