import pandas as pd

from src.validation import range_validation, validity_score


def test_invalid_numeric_values_include_parse_and_range_failures():
    frame = pd.DataFrame({"humidity": [50, -1, 120, "bad", None]})
    result = range_validation(frame)
    assert result.loc[0, "checked_count"] == 4
    assert result.loc[0, "invalid_count"] == 3
    score, _ = validity_score(frame)
    assert score == 25.0


def test_no_applicable_observations_is_unavailable():
    score, details = validity_score(pd.DataFrame({"comment": ["ok"]}))
    assert score is None
    assert "reason" in details
