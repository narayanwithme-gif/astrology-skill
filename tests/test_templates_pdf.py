#!/usr/bin/env python3
import subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

class TemplateTests(unittest.TestCase):
    def test_pdf_export_all_langs(self):
        with tempfile.TemporaryDirectory() as td:
            for lang in ("en","hi","hinglish","mr","or"):
                out=Path(td)/f"r-{lang}.pdf"
                r=subprocess.run([sys.executable,str(ROOT/"scripts/pdf_export.py"),
                    "--chart",str(ROOT/"examples/demo/chart.json"),
                    "--request",str(ROOT/"assets/request.example.json"),
                    "--name","Test User","--lang",lang,"--out",str(out)],
                    capture_output=True,text=True,cwd=ROOT)
                self.assertEqual(r.returncode,0,r.stderr)
                self.assertTrue(out.exists() and out.stat().st_size>0)

    def test_fortune_lang_flag(self):
        with tempfile.TemporaryDirectory() as td:
            r=subprocess.run([sys.executable,str(ROOT/"scripts/fortune_report.py"),
                "--chart",str(ROOT/"examples/demo/chart.json"),
                "--request",str(ROOT/"assets/request.example.json"),
                "--name","Test User","--lang","hi","--out-dir",td],
                capture_output=True,text=True,cwd=ROOT)
            self.assertEqual(r.returncode,0,r.stderr)
            html=list(Path(td).glob("*.html"))[0].read_text(encoding="utf-8")
            self.assertIn("कुंडली रिपोर्ट", html)

if __name__=="__main__":
    unittest.main()
