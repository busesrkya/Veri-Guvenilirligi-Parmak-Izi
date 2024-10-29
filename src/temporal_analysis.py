from __future__ import annotations

import numpy as np
import pandas as pd

from .profiling import completeness_score
from .validation import validity_score


def choose_frequency(timestamps: pd.Series) -> str:
    valid = pd.to_datetime(timestamps, errors="coerce").dropna()
    if valid.empty:
        return "D"
    span_days = max((valid.max() - valid.min()).days, 1)
    if span_days <= 7:
        return "D"
    if span_days <= 120:
        return "W"
    return "ME"


def analyze_temporal(
    frame: pd.DataFrame,
    timestamp_column: str = "timestamp",
    frequency: str | None = None,
) -> pd.DataFrame:
    if timestamp_column not in frame.columns or frame.empty:
        return pd.DataFrame()
    working = frame.copy()
    working[timestamp_column] = pd.to_datetime(working[timestamp_column], errors="coerce")
    working = working.dropna(subset=[timestamp_column]).sort_values(timestamp_column)
    if working.empty:
        return pd.DataFrame()
    frequency = frequency or choose_frequency(working[timestamp_column])
    rows = []
    for period, group in working.groupby(pd.Grouper(key=timestamp_column, freq=frequency)):
        if group.empty:
            continue
        evaluated = group.drop(columns=[timestamp_column])
        completeness, _ = completeness_score(evaluated)
        validity, _ = validity_score(evaluated)
        available = [x for x in (completeness, validity) if x is not None]
        rows.append(
            {
                "period_start": period,
                "period_end": group[timestamp_column].max(),
                "sample_size": len(group),
                "completeness": completeness,
                "validity": validity,
                "reliability_score": float(np.mean(available)) if available else np.nan,
            }
        )
    return pd.DataFrame(rows)


def temporal_stability_score(results: pd.DataFrame) -> tuple[float | None, dict]:
    if results.empty or results["reliability_score"].notna().sum() < 2:
        return None, {"reason": "En az iki zamansal dönem gerekli"}
    values = results["reliability_score"].dropna().to_numpy()
    variability = float(np.std(values, ddof=1))
    deterioration = max(0.0, float(values[0] - values[-1]))
    score = max(0.0, 100.0 - 2.5 * variability - deterioration)
    return score, {
        "periods": len(values),
        "standard_deviation_points": variability,
        "start_to_end_deterioration_points": deterioration,
        "formula": "max(0, 100 - 2,5*dönem std - pozitif başlangıç/bitiş kötüleşmesi)",
    }
