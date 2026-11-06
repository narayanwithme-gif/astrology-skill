#!/usr/bin/env python3
import copy, importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("chart_engine", ROOT/"scripts/chart_engine.py")
engine=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(engine)
EXAMPLE=json.loads((ROOT/"assets/request.example.json").read_text(encoding="utf-8"))

class AyanamshaTests(unittest.TestCase):
    def test_kp_alias(self):
        req=copy.deepcopy(EXAMPLE); req["settings"]["ayanamsha"]="kp"
        r=engine.calculate(req)
        self.assertEqual(r["provenance"]["settings"]["ayanamsha"],"krishnamurti")

    def test_raman_and_lahiri_differ(self):
        outs=[]
        for mode in ("lahiri","kp","raman"):
            req=copy.deepcopy(EXAMPLE); req["settings"]["ayanamsha"]=mode
            outs.append(engine.calculate(req)["jyotisha"]["planets"]["Sun"]["longitude"])
        self.assertNotEqual(outs[0], outs[2])

    def test_kp_uppercase(self):
        req=copy.deepcopy(EXAMPLE); req["settings"]["ayanamsha"]="KP"
        r=engine.calculate(req)
        self.assertEqual(r["provenance"]["settings"]["ayanamsha"],"krishnamurti")

if __name__=="__main__":
    unittest.main()
