from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .profiling import completeness_score, uniqueness_score
from .validation import validity_score


def _group_reliability(group: pd.DataFrame, value_column: str) -> tuple[float, dict]:
    evaluated = group.drop(columns=[value_column], errors="ignore")
    metrics = [completeness_score(evaluated)[0], validity_score(evaluated)[0], uniqueness_score(evaluated)[0]]
    available = [value for value in metrics if value is not None]
    return float(np.mean(available)), {"component_count": len(available)}


def analyze_context(
    frame: pd.DataFrame,
    context_columns: list[str],
    min_group_size: int = 30,
    max_groups_per_column: int = 50,
) -> pd.DataFrame:
    rows: list[dict] = []
    for column in context_columns:
        if column not in frame.columns:
            continue
        counts = frame[column].value_counts(dropna=False).head(max_groups_per_column)
        group_count = len(counts)
        alpha = 0.05 / max(group_count, 1)
        for value, count in counts.items():
            mask = frame[column].isna() if pd.isna(value) else frame[column].eq(value)
            group = frame.loc[mask]
            score, details = _group_reliability(group, column)
            # Wilson interval for the observed-cell completeness proportion.
            cells = max(group.drop(columns=[column]).size, 1)
            p = 1.0 - group.drop(columns=[column]).isna().sum().sum() / cells
            z = 1.96
            half_width = z * math.sqrt(max(p * (1 - p), 0) / cells)
            rows.append(
                {
                    "context_column": column,
                    "context_value": "<MISSING>" if pd.isna(value) else str(value),
                    "sample_size": int(count),
                    "reliability_score": score,
                    "missing_rate": float(1 - p),
                    "completeness_ci_low": max(0.0, p - half_width),
                    "completeness_ci_high": min(1.0, p + half_width),
                    "sufficient_sample": bool(count >= min_group_size),
                    "multiplicity_alpha": alpha,
                    **details,
                }
            )
    return pd.DataFrame(rows)


def context_stability_score(results: pd.DataFrame, min_group_size: int = 30) -> tuple[float | None, dict]:
    if results.empty:
        return None, {"reason": "Analiz edilen bağlam kolonu yok"}
    valid = results[results["sample_size"] >= min_group_size]
    if len(valid) < 2:
        return None, {"reason": "Yeterli büyüklükte ikiden az bağlam grubu var"}
    weighted_mean = np.average(valid["reliability_score"], weights=valid["sample_size"])
    weighted_variance = np.average(
        (valid["reliability_score"] - weighted_mean) ** 2,
        weights=valid["sample_size"],
    )
    weighted_std = float(np.sqrt(weighted_variance))
    score = max(0.0, 100.0 - 3.0 * weighted_std)
    return score, {
        "eligible_groups": len(valid),
        "weighted_std_points": weighted_std,
        "formula": "max(0, 100 - 3 * grup güvenilirliğinin ağırlıklı standart sapması)",
    }
