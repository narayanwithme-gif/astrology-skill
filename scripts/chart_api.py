#!/usr/bin/env python3
"""Small localhost JSON API for the chart calculator; request bodies are not logged."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

import chart_engine


class ChartHandler(BaseHTTPRequestHandler):
    server_version = "HermesAstrology/1"

    def do_POST(self):
        if self.path != "/chart":
            self.send_error(404, "Use POST /chart")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 1_000_000:
                raise ValueError("Request body must be between 1 byte and 1 MB")
            request = json.loads(self.rfile.read(length))
            result = chart_engine.calculate(request)
            body = json.dumps(result, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            body = json.dumps({"error": str(exc)}).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, format, *args):
        # Default access logs can expose birth details embedded in query strings.
        return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        parser.error("The API binds to localhost only to keep birth data on this machine")
    server = HTTPServer((args.host, args.port), ChartHandler)
    print(f"Local chart API listening at http://{args.host}:{args.port}/chart")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
