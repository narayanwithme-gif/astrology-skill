# SPDX-License-Identifier: AGPL-3.0-or-later
"""Calculation conventions and CLI behavior with fictional input."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("chart_engine", ROOT / "scripts/chart_engine.py")
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)
EXAMPLE = json.loads((ROOT / "assets/request.example.json").read_text(encoding="utf-8"))


class CalculationTests(unittest.TestCase):
    def setUp(self):
        self.request = copy.deepcopy(EXAMPLE)

    def test_utc_and_chart_invariants(self):
        result = engine.calculate(self.request)
        self.assertEqual(result["provenance"]["birth_utc"], "2000-01-01T06:30:00+00:00")
        self.assertTrue(all(result["internal_checks"].values()))
        for key in ["western", "jyotisha"]:
            chart = result[key]
            self.assertEqual(len(chart["cusps"]), 12)
            for planet in chart["planets"].values():
                self.assertTrue(0 <= planet["longitude"] < 360)
                self.assertTrue(1 <= planet["house"] <= 12)

    def test_varga_sign_starts_and_part_boundary(self):
        for sign in range(12):
            with self.subTest(sign=sign):
                expected = (sign + [0, 8, 4][sign % 3]) % 12
                self.assertEqual(int(engine.varga_longitude(sign * 30, 9) // 30), expected)
                start = sign if sign % 2 == 0 else (sign + 8) % 12
                self.assertEqual(int(engine.varga_longitude(sign * 30, 10) // 30), start)
                self.assertEqual(
                    int(engine.varga_longitude(sign * 30 + 3, 10) // 30), (start + 1) % 12
                )

    def test_house_boundaries(self):
        cusps = [i * 30 for i in range(12)]
        for i in range(12):
            self.assertEqual(engine.house_of(i * 30, cusps), i + 1)
        self.assertEqual(engine.house_of(359.999, cusps), 12)

    def test_period_partition(self):
        result = engine.calculate(self.request)
        for md in result["vimshottari"]["mahadashas"]:
            self.assertEqual(md["antardashas"][0]["lord"], md["lord"])
            end = engine.datetime.fromisoformat(md["end_utc"])
            ad_end = engine.datetime.fromisoformat(md["antardashas"][-1]["end_utc"])
            self.assertLess(abs((end - ad_end).total_seconds()), 0.001)
            for left, right in zip(md["antardashas"], md["antardashas"][1:]):
                self.assertEqual(left["end_utc"], right["start_utc"])

    def test_birth_dasha_lord_and_balance(self):
        birth = engine.datetime(2000, 1, 1, tzinfo=engine.UTC)
        dasha = engine.dashas(birth, (360 / 27) * 2.5, birth, 365.25)
        self.assertEqual(dasha["birth_lord"], "Sun")
        self.assertAlmostEqual(dasha["birth_balance_years"], 3)

    def test_dst_gap_rejected(self):
        self.request["birth"].update(date="2024-03-10", time="02:30", timezone="America/New_York")
        with self.assertRaisesRegex(ValueError, "Nonexistent"):
            engine.calculate(self.request)

    def test_dst_fold_requires_choice(self):
        self.request["birth"].update(date="2024-11-03", time="01:30", timezone="America/New_York")
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            engine.calculate(self.request)
        self.request["birth"]["fold"] = 0
        first = engine.parse_birth(self.request["birth"]).astimezone(engine.UTC)
        self.request["birth"]["fold"] = 1
        second = engine.parse_birth(self.request["birth"]).astimezone(engine.UTC)
        self.assertEqual((second - first).total_seconds(), 3600)

    def test_invalid_coordinates(self):
        for key, value in [("latitude", float("nan")), ("longitude", 181), ("latitude", True)]:
            with self.subTest(key=key, value=value):
                req = copy.deepcopy(self.request)
                req["birth"][key] = value
                with self.assertRaises(ValueError):
                    engine.calculate(req)

    def test_snapshot_requires_offset(self):
        self.request["as_of"] = "2026-11-03T12:00"
        with self.assertRaisesRegex(ValueError, "offset"):
            engine.calculate(self.request)

    def test_unsupported_settings_rejected(self):
        for key, value in [("western_houses", "Z"), ("ayanamsha", "unknown"), ("nodes", "unknown")]:
            with self.subTest(key=key):
                req = copy.deepcopy(self.request)
                req["settings"][key] = value
                with self.assertRaises(ValueError):
                    engine.calculate(req)

    def test_polar_house_failure(self):
        self.request["birth"]["latitude"] = 89
        with self.assertRaises(engine.swe.Error):
            engine.calculate(self.request)

    def test_supported_alternatives(self):
        for houses in ["W", "E", "K", "O"]:
            with self.subTest(houses=houses):
                req = copy.deepcopy(self.request)
                req["settings"].update(western_houses=houses, nodes="true", ayanamsha="raman")
                result = engine.calculate(req)
                self.assertEqual(result["western"]["house_method"], houses)
                self.assertTrue(all(result["internal_checks"].values()))
        self.request["settings"]["ayanamsha"] = "krishnamurti"
        self.assertTrue(all(engine.calculate(self.request)["internal_checks"].values()))

    def test_transit_traditions_are_distinct(self):
        result = engine.calculate(self.request)
        self.assertIn("major_aspect_snapshot", result["transits"]["western"])
        self.assertNotIn("major_aspect_snapshot", result["transits"]["jyotisha"])
        sidereal = result["transits"]["jyotisha"]
        self.assertEqual(len(sidereal["graha_drishti_to_natal"]), 13)
        self.assertIn("Ketu", sidereal["planets"])
        self.assertTrue(all("natal_rashi_house" in p for p in sidereal["planets"].values()))

    def test_uncertainty_endpoints(self):
        points = engine.calculate(self.request)["uncertainty"]["endpoints"]
        self.assertEqual([p["offset_minutes"] for p in points], [-5, 5])
        span = engine.datetime.fromisoformat(points[1]["utc"]) - engine.datetime.fromisoformat(
            points[0]["utc"]
        )
        self.assertEqual(span.total_seconds(), 600)

    def test_html_escapes_labels(self):
        self.request["label"] = '<script>alert("x")</script>'
        document = engine.atlas(engine.calculate(self.request))
        self.assertNotIn("<script>", document)
        self.assertIn("&lt;script&gt;", document)
        self.assertNotIn("<script src=", document)


class CommandTests(unittest.TestCase):
    def run_cli(self, request, out, temp):
        source = Path(temp) / "input.json"
        source.write_text(json.dumps(request), encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/chart_engine.py"),
                "--input",
                str(source),
                "--out",
                str(out),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_cli_writes_report_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "report"
            result = self.run_cli(EXAMPLE, out, temp)
            self.assertEqual(result.returncode, 0, result.stderr)
            original = (out / "chart.json").read_bytes()
            self.assertEqual(json.loads(result.stdout)["status"], "computed")
            self.assertTrue((out / "charts.html").is_file())
            self.assertTrue((out / "calculation.md").is_file())
            second = self.run_cli(EXAMPLE, out, temp)
            self.assertEqual(second.returncode, 2)
            self.assertEqual((out / "chart.json").read_bytes(), original)

    def test_cli_rejects_bad_input_without_report(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "report"
            request = copy.deepcopy(EXAMPLE)
            request["birth"]["latitude"] = 200
            result = self.run_cli(request, out, temp)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stderr)["status"], "error")
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
