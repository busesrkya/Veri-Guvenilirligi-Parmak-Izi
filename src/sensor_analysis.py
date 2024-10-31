from __future__ import annotations

import numpy as np
import pandas as pd


def analyze_sensor_consistency(
    frame: pd.DataFrame,
    target: str = "vibration",
    predictors: list[str] | None = None,
    rolling_window: int = 48,
) -> dict:
    predictors = predictors or ["machine_load", "temperature", "pressure"]
    selected = [c for c in predictors if c in frame.columns]
    if target not in frame.columns or len(selected) < 1:
        return {"available": False, "reason": "Hedef veya açıklayıcı sensör kolonları eksik"}
    working = frame[selected + [target]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(working) < 50:
        return {"available": False, "reason": "En az 50 eksiksiz gözlem gerekli"}
    x = working[selected].to_numpy(dtype=float)
    y = working[target].to_numpy(dtype=float)
    design = np.column_stack([np.ones(len(x)), x])
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    prediction = design @ coefficients
    residuals = pd.Series(y - prediction, index=working.index)
    residual_median = residuals.median()
    residual_mad = (residuals - residual_median).abs().median()
    if residual_mad == 0:
        anomalous = pd.Series(False, index=working.index)
    else:
        robust_z = 0.6745 * (residuals - residual_median).abs() / residual_mad
        anomalous = robust_z > 4.5
    rolling_mean = working[target].rolling(rolling_window, min_periods=max(10, rolling_window // 4)).mean()
    rolling_std = working[target].rolling(rolling_window, min_periods=max(10, rolling_window // 4)).std()
    rolling_deviation = ((working[target] - rolling_mean).abs() > 4 * rolling_std).fillna(False)
    return {
        "available": True,
        "rows_used": len(working),
        "target": target,
        "predictors": selected,
        "r_squared": float(1.0 - np.sum((y - prediction) ** 2) / np.sum((y - y.mean()) ** 2)) if np.var(y) > 0 else 0.0,
        "residual_anomaly_count": int(anomalous.sum()),
        "residual_anomaly_rate": float(anomalous.mean()),
        "rolling_deviation_count": int(rolling_deviation.sum()),
        "correlations": working.corr().round(4).to_dict(),
        "interpretation": "İşaretler olası ölçüm tutarsızlıklarıdır; doğrulanmış ekipman arızası değildir.",
    }
