from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def generate_clean_sensor_data(row_count: int = 36_000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2025-01-01", periods=row_count, freq="10min")
    machine_id = rng.choice([f"M{i:02d}" for i in range(1, 13)], row_count)
    sensor_id = np.array([f"S{(int(value[1:]) - 1) % 6 + 1:02d}" for value in machine_id])
    hours = timestamps.hour.to_numpy()
    shift = np.select([hours < 8, hours < 16], ["night", "morning"], default="evening")
    status = rng.choice(["normal", "high_load", "idle"], row_count, p=[0.68, 0.24, 0.08])
    machine_effect = np.array([int(value[1:]) * 0.6 for value in machine_id])
    status_load = pd.Series(status).map({"normal": 0, "high_load": 20, "idle": -35}).to_numpy()
    machine_load = np.clip(55 + status_load + machine_effect + rng.normal(0, 9, row_count), 4, 100)
    operating_speed = np.clip(900 + 28 * machine_load + rng.normal(0, 220, row_count), 200, 4100)
    ambient_cycle = 5 * np.sin(2 * np.pi * hours / 24)
    temperature = 28 + 0.36 * machine_load + ambient_cycle + 0.15 * machine_effect + rng.normal(0, 3.2, row_count)
    pressure = 2.2 + 0.055 * machine_load + rng.normal(0, 0.55, row_count)
    vibration = 0.8 + 0.055 * machine_load + 0.0003 * operating_speed + rng.normal(0, 0.6, row_count)
    humidity = np.clip(58 - 0.32 * ambient_cycle + rng.normal(0, 8, row_count), 15, 95)
    risk = -7.2 + 0.065 * temperature + 0.48 * vibration + 0.016 * machine_load
    probability = 1 / (1 + np.exp(-risk))
    quality_label = np.where(rng.random(row_count) < probability, "attention", "normal")
    return pd.DataFrame(
        {
            "record_id": np.arange(1, row_count + 1),
            "timestamp": timestamps,
            "machine_id": machine_id,
            "sensor_id": sensor_id,
            "shift": shift,
            "temperature": temperature.round(3),
            "pressure": pressure.round(3),
            "vibration": vibration.round(3),
            "humidity": humidity.round(3),
            "operating_speed": operating_speed.round(3),
            "machine_load": machine_load.round(3),
            "operating_status": status,
            "quality_label": quality_label,
        }
    )


def inject_quality_issues(clean: pd.DataFrame, seed: int = 43) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Inject controlled defects and return a separate evaluation-only event log."""
    rng = np.random.default_rng(seed)
    frame = clean.copy()
    events: list[dict] = []

    def register(indices, issue: str, column: str) -> None:
        for index in np.asarray(indices):
            events.append({"record_id": int(frame.at[index, "record_id"]), "issue_type": issue, "column": column})

    night_m09 = frame.index[(frame["shift"] == "night") & (frame["machine_id"] == "M09")]
    missing_idx = rng.choice(night_m09, size=max(1, int(len(night_m09) * 0.34)), replace=False)
    register(missing_idx, "context_missingness", "vibration")
    frame.loc[missing_idx, "vibration"] = np.nan

    general_missing = rng.choice(frame.index, size=int(len(frame) * 0.018), replace=False)
    missing_columns = rng.choice(["temperature", "pressure", "humidity", "machine_load"], len(general_missing))
    for column in np.unique(missing_columns):
        selected = general_missing[missing_columns == column]
        register(selected, "random_missingness", column)
        frame.loc[selected, column] = np.nan

    spike_idx = rng.choice(frame.index, size=int(len(frame) * 0.009), replace=False)
    register(spike_idx, "sensor_spike", "vibration")
    frame.loc[spike_idx, "vibration"] = frame.loc[spike_idx, "vibration"] * rng.uniform(4, 9, len(spike_idx))

    invalid_idx = rng.choice(frame.index.difference(spike_idx), size=int(len(frame) * 0.004), replace=False)
    register(invalid_idx, "invalid_measurement", "humidity")
    frame.loc[invalid_idx, "humidity"] = rng.choice([-12.0, 135.0], len(invalid_idx))

    drift_start = int(len(frame) * 0.78)
    drift_idx = frame.index[drift_start:]
    register(drift_idx, "distribution_shift", "temperature")
    frame.loc[drift_idx, "temperature"] = frame.loc[drift_idx, "temperature"] + np.linspace(0, 10, len(drift_idx))

    m04_rows = frame.index[frame["machine_id"] == "M04"]
    inconsistent = rng.choice(m04_rows, size=min(300, len(m04_rows)), replace=False)
    register(inconsistent, "sensor_inconsistency", "pressure")
    frame.loc[inconsistent, "pressure"] = rng.normal(11.5, 0.8, len(inconsistent))

    duplicate_idx = rng.choice(frame.index, size=int(len(frame) * 0.006), replace=False)
    duplicate_rows = frame.loc[duplicate_idx].copy()
    for record_id in duplicate_rows["record_id"]:
        events.append({"record_id": int(record_id), "issue_type": "duplicate_record", "column": "<row>"})
    frame = pd.concat([frame, duplicate_rows], ignore_index=True)
    return frame, pd.DataFrame(events)


def generate_files(output_dir: Path, row_count: int = 36_000, seed: int = 42) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    clean = generate_clean_sensor_data(row_count=row_count, seed=seed)
    observed, reference = inject_quality_issues(clean, seed=seed + 1)
    data_path = output_dir / "sample_data.csv"
    reference_path = output_dir / "synthetic_error_reference.csv"
    observed.to_csv(data_path, index=False)
    reference.to_csv(reference_path, index=False)
    return data_path, reference_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yeniden üretilebilir endüstriyel sensör verisi oluştur")
    parser.add_argument("--rows", type=int, default=36_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    paths = generate_files(args.output_dir, args.rows, args.seed)
    print(f"{paths[0]} ve yalnızca değerlendirme amaçlı {paths[1]} oluşturuldu")
