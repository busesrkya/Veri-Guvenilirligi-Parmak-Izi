import pandas as pd

from src.temporal_analysis import analyze_temporal, temporal_stability_score


def test_missing_timestamp_returns_empty(small_sensor_frame):
    assert analyze_temporal(small_sensor_frame.drop(columns="timestamp")).empty


def test_temporal_decline_is_reflected(small_sensor_frame):
    frame = small_sensor_frame.copy()
    frame.loc[80:, "humidity"] = None
    result = analyze_temporal(frame, frequency="D")
    score, details = temporal_stability_score(result)
    assert score is not None and score < 100
    assert details["periods"] >= 2
