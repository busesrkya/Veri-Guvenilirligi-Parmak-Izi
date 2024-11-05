from __future__ import annotations

from collections.abc import Mapping

from .config import DEFAULT_WEIGHTS


def calculate_overall_score(
    metrics: Mapping[str, float | None],
    weights: Mapping[str, float] | None = None,
) -> dict:
    active_weights = dict(DEFAULT_WEIGHTS if weights is None else weights)
    unknown = set(active_weights) - set(metrics)
    if unknown:
        raise ValueError(f"Ağırlıklar bilinmeyen metriklere başvuruyor: {sorted(unknown)}")
    used = {
        name: float(value)
        for name, value in metrics.items()
        if value is not None and name in active_weights and active_weights[name] > 0
    }
    for name, value in used.items():
        if not 0 <= value <= 100:
            raise ValueError(f"{name!r} metriği 0 ile 100 arasında olmalı")
    denominator = sum(active_weights[name] for name in used)
    overall = None if denominator == 0 else sum(used[n] * active_weights[n] for n in used) / denominator
    return {
        "overall_score": overall,
        "used_metrics": list(used),
        "unavailable_metrics": [name for name, value in metrics.items() if value is None],
        "normalized_weights": (
            {} if denominator == 0 else {name: active_weights[name] / denominator for name in used}
        ),
    }
