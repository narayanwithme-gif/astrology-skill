import json
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import chart_api

ROOT = Path(__file__).resolve().parents[1]


class ChartApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), chart_api.ChartHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/chart"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, payload):
        request = Request(
            self.url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return urlopen(request)

    def test_calculates_example_chart(self):
        payload = json.loads((ROOT / "assets/request.example.json").read_text())
        with self.post(payload) as response:
            result = json.load(response)
        self.assertIn("western", result)
        self.assertIn("jyotisha", result)

    def test_invalid_request_returns_json_400(self):
        with self.assertRaises(HTTPError) as raised:
            self.post({})
        self.assertEqual(raised.exception.code, 400)
        self.assertIn("error", json.load(raised.exception))


if __name__ == "__main__":
    unittest.main()
