import numpy as np
import pandas as pd

from src.ml_experiments import FEATURES, _pipeline, run_experiments


def test_preprocessing_is_fit_only_on_training_data(small_sensor_frame):
    train = small_sensor_frame.iloc[:80].copy()
    test = small_sensor_frame.iloc[80:].copy()
    train["temperature"] = np.arange(80, dtype=float)
    test["temperature"] = 10000.0
    numeric = [c for c in FEATURES if pd.api.types.is_numeric_dtype(train[c])]
    categorical = [c for c in FEATURES if c not in numeric]
    pipeline = _pipeline("logistic_regression", numeric, categorical, 42)
    pipeline.fit(train[FEATURES], train["quality_label"])
    scaler = pipeline.named_steps["preprocessing"].named_transformers_["numeric"].named_steps["scale"]
    temperature_index = numeric.index("temperature")
    assert scaler.mean_[temperature_index] == np.mean(np.arange(80, dtype=float))
    assert scaler.mean_[temperature_index] != 10000.0


def test_experiments_produce_all_models_and_scenarios(small_sensor_frame):
    result = run_experiments(small_sensor_frame, seed=7)
    assert len(result) == 8
    assert set(result["model"]) == {"logistic_regression", "random_forest"}
    assert result["f1_score"].between(0, 1).all()
    assert set(result["random_seed"]) == {7}
