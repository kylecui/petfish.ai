"""Stdlib HTTP server for PEtFiSh Online Gateway.

This server is intended for local smoke tests and simple Gateway Mode deployment
experiments. It implements the same operation surface as actions/openapi.yaml
without requiring FastAPI or other framework dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Tuple

GATEWAY_DIR = Path(__file__).resolve().parent
if str(GATEWAY_DIR) not in sys.path:
    sys.path.insert(0, str(GATEWAY_DIR))

from app import dispatch  # noqa: E402
from schemas import envelope  # noqa: E402

ROUTE_TO_OPERATION = {
    "/healthz": "healthz",
    "/v1/kernel/route": "routeCompanionRequest",
    "/v1/catalog/search": "searchCatalog",
    "/v1/catalog/suggest": "suggestPacks",
    "/v1/install/render": "renderInstallCommand",
    "/v1/project/profile": "profileProject",
    "/v1/skill/design": "designSkill",
    "/v1/trust/classify": "classifyActionRisk",
    "/v1/remote/preview": "previewRemoteExecution",
    "/v1/remote/execute": "executeRemoteCommand",
}


class GatewayHandler(BaseHTTPRequestHandler):
    server_version = "PEtFiShOnlineGateway/0.1"

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path == "/healthz":
            self._write_json(200, {"ok": True, "service": "petfish-online-gateway"})
            return
        self._write_json(404, _error("gateway", "not_found", f"Unknown GET path: {self.path}"))

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        operation = ROUTE_TO_OPERATION.get(self.path)
        if not operation or operation == "healthz":
            self._write_json(404, _error("gateway", "not_found", f"Unknown POST path: {self.path}"))
            return

        ok, payload_or_error = self._read_json()
        if not ok:
            self._write_json(400, _error("gateway", "bad_json", str(payload_or_error)))
            return

        try:
            result = dispatch(operation, payload_or_error)
        except Exception as exc:  # pragma: no cover - visible during local smoke testing
            result = _error(
                "gateway",
                "dispatch_error",
                str(exc),
                data={"operation": operation, "traceback": traceback.format_exc(limit=5)},
            )
            self._write_json(500, result)
            return

        self._write_json(200, result)

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[online-gpt-gateway] " + fmt % args + "\n")

    def _read_json(self) -> Tuple[bool, Dict[str, Any] | str]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return True, {}
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            return False, f"Invalid JSON: {exc}"
        if not isinstance(data, dict):
            return False, "JSON payload must be an object"
        return True, data

    def _write_json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def _error(module: str, code: str, message: str, data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return envelope(
        ok=False,
        module=module,
        mode="dry_run",
        result_level="advice_only",
        data=data or {},
        errors=[code, message],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PEtFiSh Online Gateway stdlib server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), GatewayHandler)
    print(f"PEtFiSh Online Gateway listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping PEtFiSh Online Gateway")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
