from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from clickpe_pim.evaluate import evaluate_database
from clickpe_pim.pipeline import run_monitor
from clickpe_pim.report import build_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="clickpe_pim")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--config", type=Path, default=Path("config.yaml"))
    run.add_argument("--mode", choices=["live", "replay"], required=True)
    run.add_argument("--manifest", type=Path)
    run.add_argument("--output-root", type=Path, default=Path("."))
    run.add_argument("--run-id")
    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--db", type=Path, required=True)
    evaluate.add_argument("--labels", type=Path, required=True)
    evaluate.add_argument("--split", choices=["dev", "test"], required=True)
    evaluate.add_argument("--output", type=Path, required=True)
    report = sub.add_parser("report")
    report.add_argument("--db", type=Path, required=True)
    report.add_argument("--evaluation", type=Path, required=True)
    report.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "run":
            result = run_monitor(args.config, mode=args.mode, replay_manifest=args.manifest, output_root=args.output_root, run_id=args.run_id)
            print(json.dumps(asdict(result), sort_keys=True))
            return 0 if result.status == "complete" else 2
        if args.command == "evaluate":
            output = evaluate_database(args.db, args.labels, args.split)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(json.dumps(output, sort_keys=True))
            return 0
        evaluation = json.loads(args.evaluation.read_text(encoding="utf-8"))
        print(build_report(args.db, evaluation, args.output_dir))
        return 0
    except (ValueError, OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, sort_keys=True))
        return 1

