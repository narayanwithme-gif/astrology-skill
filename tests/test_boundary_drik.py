#!/usr/bin/env python3
import copy, importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

class BoundaryTests(unittest.TestCase):
    def test_boundary_check_stable(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "b.json"
            r = subprocess.run([sys.executable, str(ROOT / "scripts" / "boundary_check.py"),
                "--request", str(ROOT / "assets" / "request.example.json"), "--window-minutes", "3", "--out", str(out)],
                capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("is_cusp_sensitive", data)

    def test_drik_ayanamsha(self):
        SPEC = importlib.util.spec_from_file_location("chart_engine", ROOT / "scripts" / "chart_engine.py")
        eng = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(eng)
        req = json.loads((ROOT / "assets" / "request.example.json").read_text(encoding="utf-8"))
        req["settings"]["ayanamsha"] = "drik"
        r = eng.calculate(copy.deepcopy(req))
        self.assertEqual(r["provenance"]["settings"]["ayanamsha"], "drik")

if __name__ == "__main__":
    unittest.main()
