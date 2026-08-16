from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .config import load_site_config, repository_root
from .control import SupervisoryController
from .evidence import build_evidence_bundle
from .models import Telemetry
from .simulation import simulate_reference_day
from .sizing import size_site


class CoolRideRequestHandler(BaseHTTPRequestHandler):
    server_version = "CoolRidePQ/0.1"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        config = load_site_config()
        if path == "/api/health":
            self._json({"status": "ok", "version": "0.1.0", "actuation": "disabled"})
            return
        if path == "/api/site/sizing":
            self._json(size_site(config).to_dict())
            return
        if path == "/api/scenario":
            self._json(simulate_reference_day(config))
            return
        if path == "/api/evidence":
            scenario = simulate_reference_day(config)
            self._json(build_evidence_bundle(config, scenario))
            return
        self._serve_static(path)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/api/control/decision":
            self._json({"error": "not_found"}, HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 1_000_000:
            self._json({"error": "invalid_content_length"}, HTTPStatus.BAD_REQUEST)
            return
        try:
            payload = json.loads(self.rfile.read(length))
            telemetry = Telemetry.from_dict(payload)
            decision = SupervisoryController(load_site_config(), advisory_only=True).decide(telemetry)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            self._json({"error": "invalid_request", "detail": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        self._json(decision.to_dict())

    def log_message(self, format: str, *args: object) -> None:
        print(f"coolride-pq-api: {format % args}")

    def _json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _serve_static(self, path: str) -> None:
        web_root = repository_root() / "apps" / "ops-console"
        requested = "index.html" if path == "/" else path.lstrip("/")
        candidate = (web_root / requested).resolve()
        if web_root.resolve() not in candidate.parents and candidate != web_root.resolve():
            self._json({"error": "invalid_path"}, HTTPStatus.BAD_REQUEST)
            return
        if not candidate.is_file():
            self._json({"error": "not_found"}, HTTPStatus.NOT_FOUND)
            return
        content_types = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".svg": "image/svg+xml",
        }
        content = candidate.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_types.get(candidate.suffix, "application/octet-stream"))
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def serve(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = ThreadingHTTPServer((host, port), CoolRideRequestHandler)
    print(f"CoolRide-PQ advisory console: http://{host}:{port}")
    print("Actuation is disabled. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
