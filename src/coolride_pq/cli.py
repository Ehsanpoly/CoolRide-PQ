from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .config import load_site_config
from .control import SupervisoryController
from .evidence import build_evidence_bundle
from .models import Telemetry
from .server import serve
from .simulation import simulate_reference_day
from .sizing import size_site


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    scalar_keys = [
        key for key, value in rows[0].items() if not isinstance(value, (list, dict, tuple))
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=scalar_keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in scalar_keys})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="coolride-pq")
    parser.add_argument("--config", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("size", help="size the configured reference site")
    simulate = subparsers.add_parser("simulate", help="run the deterministic reference day")
    simulate.add_argument("--json", type=Path, default=None)
    simulate.add_argument("--csv", type=Path, default=None)
    evidence = subparsers.add_parser("evidence", help="emit the evidence manifest")
    evidence.add_argument("--json", type=Path, default=None)
    decision = subparsers.add_parser("decision", help="evaluate one telemetry JSON object")
    decision.add_argument("telemetry", type=Path)
    run_server = subparsers.add_parser("serve", help="run the local API and console")
    run_server.add_argument("--host", default="127.0.0.1")
    run_server.add_argument("--port", type=int, default=8080)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_site_config(args.config)
    if args.command == "size":
        print(json.dumps(size_site(config).to_dict(), indent=2))
        return 0
    if args.command == "simulate":
        scenario = simulate_reference_day(config)
        if args.json:
            _write_json(args.json, scenario)
        if args.csv:
            _write_csv(args.csv, scenario["rows"])
        print(json.dumps(scenario["metrics"], indent=2))
        return 0
    if args.command == "evidence":
        evidence = build_evidence_bundle(config, simulate_reference_day(config))
        if args.json:
            _write_json(args.json, evidence)
        print(json.dumps(evidence, indent=2))
        return 0
    if args.command == "decision":
        telemetry = Telemetry.from_dict(json.loads(args.telemetry.read_text(encoding="utf-8")))
        decision = SupervisoryController(config, advisory_only=True).decide(telemetry)
        print(json.dumps(decision.to_dict(), indent=2))
        return 0
    if args.command == "serve":
        serve(args.host, args.port)
        return 0
    return 2
