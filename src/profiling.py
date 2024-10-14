from __future__ import annotations

import numpy as np
import pandas as pd


def profile_dataset(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {
            "row_count": 0,
            "column_count": len(frame.columns),
            "duplicate_rows": 0,
            "missing_cells": 0,
            "columns": [],
        }
    columns = []
    for column in frame.columns:
        series = frame[column]
        columns.append(
            {
                "column": column,
                "dtype": str(series.dtype),
                "missing_count": int(series.isna().sum()),
                "missing_rate": float(series.isna().mean()),
                "unique_count": int(series.nunique(dropna=True)),
            }
        )
    return {
        "row_count": len(frame),
        "column_count": len(frame.columns),
        "duplicate_rows": int(frame.duplicated().sum()),
        "missing_cells": int(frame.isna().sum().sum()),
        "columns": columns,
    }


def completeness_score(frame: pd.DataFrame, columns: list[str] | None = None) -> tuple[float | None, dict]:
    selected = frame[columns] if columns else frame
    total = int(selected.shape[0] * selected.shape[1])
    if total == 0:
        return None, {"reason": "Veri setinde değerlendirilecek hücre yok"}
    missing = int(selected.isna().sum().sum())
    return 100.0 * (1.0 - missing / total), {"cells": total, "missing_cells": missing}


def uniqueness_score(frame: pd.DataFrame, key_columns: list[str] | None = None) -> tuple[float | None, dict]:
    if frame.empty:
        return None, {"reason": "Veri setinde kayıt yok"}
    subset = key_columns or None
    duplicates = int(frame.duplicated(subset=subset, keep="first").sum())
    return 100.0 * (1.0 - duplicates / len(frame)), {
        "rows": len(frame),
        "duplicate_rows": duplicates,
        "key_columns": key_columns or "tüm kolonlar",
    }


def robust_outlier_mask(series: pd.Series, threshold: float = 6.0) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    median = numeric.median()
    mad = (numeric - median).abs().median()
    if pd.isna(mad) or mad == 0:
        return pd.Series(False, index=series.index)
    robust_z = 0.6745 * (numeric - median).abs() / mad
    return robust_z > threshold
