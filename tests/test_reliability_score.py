import pytest

from src.reliability_score import calculate_overall_score


def test_unavailable_metric_is_excluded_not_assumed_perfect():
    result = calculate_overall_score({"completeness": 80.0, "validity": None}, {"completeness": 1, "validity": 1})
    assert result["overall_score"] == 80.0
    assert result["unavailable_metrics"] == ["validity"]
    assert result["used_metrics"] == ["completeness"]


def test_weighted_score():
    result = calculate_overall_score({"a": 80.0, "b": 100.0}, {"a": 3, "b": 1})
    assert result["overall_score"] == 85.0


def test_score_outside_range_fails():
    with pytest.raises(ValueError):
        calculate_overall_score({"a": 120.0}, {"a": 1})
