from __future__ import annotations

import argparse
import json
from pathlib import Path

from .data_loader import load_csv
from .fingerprint import analyze_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Bir CSV dosyasının veri güvenilirliği parmak izini analiz et")
    parser.add_argument("csv", type=Path)
    parser.add_argument("--name", default="dataset")
    parser.add_argument("--contexts", nargs="*", default=["machine_id", "sensor_id", "shift", "operating_status", "temperature_range", "machine_load_range"])
    parser.add_argument("--timestamp", default="timestamp")
    parser.add_argument("--ml", action="store_true")
    parser.add_argument("--report-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()
    frame = load_csv(args.csv, args.timestamp)
    result = analyze_dataset(frame, args.name, args.contexts, args.timestamp, ["record_id"] if "record_id" in frame else None)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    summary = {key: value for key, value in result.items() if not hasattr(value, "to_csv")}
    (args.report_dir / "fingerprint.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    result["context_results"].to_csv(args.report_dir / "context_results.csv", index=False)
    result["temporal_results"].to_csv(args.report_dir / "temporal_results.csv", index=False)
    result["detected_issues"].to_csv(args.report_dir / "detected_issues.csv", index=False)
    if args.ml:
        from .ml_experiments import run_experiments

        run_experiments(frame).to_csv(args.report_dir / "ml_experiments.csv", index=False)
    print(json.dumps({"dataset": args.name, "metrics": result["metrics"], "overall_score": result["overall_score"]}, indent=2))


if __name__ == "__main__":
    main()
