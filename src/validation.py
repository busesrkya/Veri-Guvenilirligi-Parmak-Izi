from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd

from .config import DEFAULT_RANGES


def range_validation(
    frame: pd.DataFrame,
    rules: Mapping[str, tuple[float, float]] | None = None,
) -> pd.DataFrame:
    """Return per-column validation counts; missing values are not validation failures."""
    active_rules = rules or DEFAULT_RANGES
    rows: list[dict] = []
    for column, (lower, upper) in active_rules.items():
        if column not in frame.columns:
            continue
        numeric = pd.to_numeric(frame[column], errors="coerce")
        observed = frame[column].notna()
        parse_failures = observed & numeric.isna()
        out_of_range = numeric.notna() & ~numeric.between(lower, upper, inclusive="both")
        checked = int(observed.sum())
        invalid = int((parse_failures | out_of_range).sum())
        rows.append(
            {
                "column": column,
                "lower": lower,
                "upper": upper,
                "checked_count": checked,
                "invalid_count": invalid,
                "valid_rate": np.nan if checked == 0 else 1.0 - invalid / checked,
            }
        )
    return pd.DataFrame(rows)


def validity_score(frame: pd.DataFrame, rules=None) -> tuple[float | None, dict]:
    result = range_validation(frame, rules)
    checked = int(result.get("checked_count", pd.Series(dtype=int)).sum())
    invalid = int(result.get("invalid_count", pd.Series(dtype=int)).sum())
    if checked == 0:
        return None, {"reason": "Yapılandırılan doğrulama kurallarına uyan gözlenen değer yok"}
    return 100.0 * (1.0 - invalid / checked), {
        "checked_values": checked,
        "invalid_values": invalid,
        "rules_evaluated": len(result),
    }
