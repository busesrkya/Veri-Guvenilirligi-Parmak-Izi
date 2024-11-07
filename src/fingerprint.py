from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd

from .context_analysis import analyze_context, context_stability_score
from .profiling import completeness_score, profile_dataset, robust_outlier_mask, uniqueness_score
from .reliability_score import calculate_overall_score
from .sensor_analysis import analyze_sensor_consistency
from .temporal_analysis import analyze_temporal, temporal_stability_score
from .validation import range_validation, validity_score


def add_derived_contexts(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    if "temperature" in enriched.columns:
        enriched["temperature_range"] = pd.cut(
            pd.to_numeric(enriched["temperature"], errors="coerce"),
            bins=[-np.inf, 40, 60, 80, np.inf],
            labels=["low", "normal", "high", "critical"],
        )
    if "machine_load" in enriched.columns:
        enriched["machine_load_range"] = pd.cut(
            pd.to_numeric(enriched["machine_load"], errors="coerce"),
            bins=[-np.inf, 30, 60, 80, np.inf],
            labels=["low", "normal", "high", "critical"],
        )
    return enriched


def detect_issues(
    frame: pd.DataFrame,
    context_columns: list[str],
    validation_results: pd.DataFrame,
    key_columns: list[str] | None,
) -> pd.DataFrame:
    rows: list[dict] = []
    for column in frame.columns:
        count = int(frame[column].isna().sum())
        if count:
            rows.append({"issue_type": "missing_value", "column_name": column, "issue_count": count,
                         "context_column": None, "context_value": None,
                         "description": f"{column} kolonunda eksik değer"})
    for item in validation_results.to_dict("records"):
        if item["invalid_count"]:
            rows.append({"issue_type": "invalid_value", "column_name": item["column"],
                         "issue_count": int(item["invalid_count"]), "context_column": None,
                         "context_value": None, "description": "Yapılandırılmış aralık dışında veya sayıya çevrilemeyen değer"})
    duplicate_count = int(frame.duplicated(subset=key_columns or None).sum())
    if duplicate_count:
        rows.append({"issue_type": "duplicate_record", "column_name": None, "issue_count": duplicate_count,
                     "context_column": None, "context_value": None,
                     "description": "Seçilen anahtara göre tekrarlanan kayıt"})
    for context in context_columns:
        if context not in frame.columns:
            continue
        evaluated = frame.drop(columns=[context], errors="ignore")
        missing_by_group = evaluated.isna().sum(axis=1).groupby(frame[context], dropna=False).sum()
        for value, count in missing_by_group.items():
            if count:
                rows.append({"issue_type": "context_missing_value", "column_name": None,
                             "issue_count": int(count), "context_column": context,
                             "context_value": "<MISSING>" if pd.isna(value) else str(value),
                             "description": "Bağlam grubundaki toplam eksik hücre"})
    return pd.DataFrame(rows)


def consistency_score(frame: pd.DataFrame, sensor_columns: list[str] | None = None) -> tuple[float | None, dict]:
    candidates = sensor_columns or ["machine_load", "vibration", "temperature", "pressure"]
    columns = [c for c in candidates if c in frame.columns]
    if len(columns) < 2 or len(frame) < 30:
        return None, {"reason": "En az iki sensör kolonu ve 30 kayıt gerekli"}
    numeric = frame[columns].apply(pd.to_numeric, errors="coerce")
    usable = numeric.dropna()
    if len(usable) < 30:
        return None, {"reason": "30'dan az eksiksiz sensör gözlemi var"}
    outlier_rates = [robust_outlier_mask(usable[c]).mean() for c in columns]
    correlations = usable.corr().abs()
    upper = correlations.where(np.triu(np.ones(correlations.shape), k=1).astype(bool)).stack()
    relationship_strength = float(upper.mean()) if len(upper) else 0.0
    residual = analyze_sensor_consistency(frame)
    residual_rate = residual.get("residual_anomaly_rate", 0.0) if residual.get("available") else 0.0
    penalty = 70.0 * float(np.mean(outlier_rates)) + 50.0 * residual_rate + 10.0 * max(0.0, 0.15 - relationship_strength)
    return max(0.0, 100.0 - penalty), {
        "rows_used": len(usable),
        "sensor_columns": columns,
        "robust_outlier_rate": float(np.mean(outlier_rates)),
        "mean_absolute_correlation": relationship_strength,
        "regression_residual_analysis": residual,
        "interpretation": "Olası ölçüm tutarsızlığı; arıza teşhisi değildir",
    }


def analyze_dataset(
    frame: pd.DataFrame,
    dataset_name: str = "dataset",
    context_columns: list[str] | None = None,
    timestamp_column: str | None = "timestamp",
    key_columns: list[str] | None = None,
    validation_rules: Mapping[str, tuple[float, float]] | None = None,
) -> dict:
    contexts = context_columns or []
    context_frame = add_derived_contexts(frame)
    context_results = analyze_context(context_frame, contexts)
    temporal_results = (
        analyze_temporal(frame, timestamp_column) if timestamp_column and timestamp_column in frame else pd.DataFrame()
    )
    validation_results = range_validation(frame, validation_rules)
    metric_pairs = {
        "completeness": completeness_score(frame),
        "validity": validity_score(frame, validation_rules),
        "consistency": consistency_score(frame),
        "uniqueness": uniqueness_score(frame, key_columns),
        "context_stability": context_stability_score(context_results),
        "temporal_stability": temporal_stability_score(temporal_results),
    }
    metrics = {name: value for name, (value, _) in metric_pairs.items()}
    aggregation = calculate_overall_score(metrics)
    return {
        "dataset_name": dataset_name,
        "profile": profile_dataset(frame),
        "metrics": metrics,
        "metric_details": {name: details for name, (_, details) in metric_pairs.items()},
        **aggregation,
        "context_results": context_results,
        "temporal_results": temporal_results,
        "validation_results": validation_results,
        "detected_issues": detect_issues(context_frame, contexts, validation_results, key_columns),
        "limitations": [
            "Skorlar uygulama varsayımlarıdır; evrensel olarak doğrulanmış güvenilirlik ölçüsü değildir.",
            "Korelasyon ve residual anomalileri tutarsızlık göstergesidir; doğrulanmış sensör arızası değildir.",
            "Çoklu bağlam karşılaştırmaları tesadüfi bulgular üretebilir; örneklem işaretleri ve düzeltilmiş alfa sağlanır.",
        ],
    }
