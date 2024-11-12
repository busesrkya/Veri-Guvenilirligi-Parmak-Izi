from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .fingerprint import analyze_dataset


FEATURES = [
    "machine_id", "sensor_id", "shift", "temperature", "pressure", "vibration",
    "humidity", "operating_speed", "machine_load", "operating_status",
]


def _corrupt(frame: pd.DataFrame, scenario: str, rng: np.random.Generator) -> pd.DataFrame:
    changed = frame.copy()
    numeric = [c for c in ["temperature", "pressure", "vibration", "humidity", "machine_load"] if c in changed]
    if scenario == "missing_10pct":
        mask = rng.random((len(changed), len(numeric))) < 0.10
        changed.loc[:, numeric] = changed[numeric].mask(mask)
    elif scenario == "noise_medium":
        for column in numeric:
            scale = changed[column].std(skipna=True) * 0.45
            changed[column] = changed[column] + rng.normal(0, scale, len(changed))
    elif scenario == "night_shift_corruption" and "shift" in changed:
        mask = changed["shift"].eq("night") & (rng.random(len(changed)) < 0.45)
        changed.loc[mask, [c for c in ["vibration", "pressure"] if c in changed]] = np.nan
    return changed


def _pipeline(model_name: str, numeric: list[str], categorical: list[str], seed: int) -> Pipeline:
    preprocessing = ColumnTransformer(
        [
            ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
            ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ]
    )
    model = (
        LogisticRegression(max_iter=700, class_weight="balanced", random_state=seed)
        if model_name == "logistic_regression"
        else RandomForestClassifier(n_estimators=100, max_depth=12, min_samples_leaf=3, class_weight="balanced", n_jobs=-1, random_state=seed)
    )
    return Pipeline([("preprocessing", preprocessing), ("model", model)])


def run_experiments(frame: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    required = set(FEATURES + ["quality_label"])
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"ML experiments require columns: {sorted(missing)}")
    ordered = frame.sort_values("timestamp") if "timestamp" in frame else frame.copy()
    split = int(len(ordered) * 0.75)
    if split == 0 or split == len(ordered):
        raise ValueError("At least four rows are required for a train/test split")
    train, test = ordered.iloc[:split].copy(), ordered.iloc[split:].copy()
    numeric = [c for c in FEATURES if pd.api.types.is_numeric_dtype(ordered[c])]
    categorical = [c for c in FEATURES if c not in numeric]
    rng = np.random.default_rng(seed)
    results = []
    for scenario in ["observed_baseline", "missing_10pct", "noise_medium", "night_shift_corruption"]:
        scenario_train = train if scenario == "observed_baseline" else _corrupt(train, scenario, rng)
        scenario_test = test if scenario == "observed_baseline" else _corrupt(test, scenario, rng)
        reliability = analyze_dataset(
            pd.concat([scenario_train, scenario_test]),
            context_columns=["shift", "machine_id"],
            timestamp_column="timestamp" if "timestamp" in ordered else None,
            key_columns=["record_id"] if "record_id" in ordered else None,
        )["overall_score"]
        for model_name in ["logistic_regression", "random_forest"]:
            pipeline = _pipeline(model_name, numeric, categorical, seed)
            pipeline.fit(scenario_train[FEATURES], scenario_train["quality_label"])
            prediction = pipeline.predict(scenario_test[FEATURES])
            precision, recall, f1, _ = precision_recall_fscore_support(
                scenario_test["quality_label"], prediction, average="macro", zero_division=0
            )
            results.append(
                {
                    "scenario": scenario,
                    "model": model_name,
                    "reliability_score": reliability,
                    "accuracy": accuracy_score(scenario_test["quality_label"], prediction),
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1,
                    "confusion_matrix": json.dumps(confusion_matrix(scenario_test["quality_label"], prediction).tolist()),
                    "random_seed": seed,
                    "train_rows": len(scenario_train),
                    "test_rows": len(scenario_test),
                }
            )
    return pd.DataFrame(results)
