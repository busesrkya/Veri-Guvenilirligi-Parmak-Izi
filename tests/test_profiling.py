import pandas as pd
import pytest

from src.profiling import completeness_score, profile_dataset, uniqueness_score


def test_empty_dataset_is_not_scored():
    score, details = completeness_score(pd.DataFrame())
    assert score is None
    assert "reason" in details


def test_fully_missing_column_lowers_completeness():
    frame = pd.DataFrame({"a": [1, 2], "b": [None, None]})
    score, _ = completeness_score(frame)
    assert score == 50.0


def test_duplicate_rows_are_detected():
    frame = pd.DataFrame({"a": [1, 1, 2]})
    score, details = uniqueness_score(frame)
    assert details["duplicate_rows"] == 1
    assert score == pytest.approx(100 * (2 / 3))
    assert profile_dataset(frame)["duplicate_rows"] == 1


def test_constant_values_profile_safely():
    profile = profile_dataset(pd.DataFrame({"value": [7, 7, 7]}))
    assert profile["columns"][0]["unique_count"] == 1
