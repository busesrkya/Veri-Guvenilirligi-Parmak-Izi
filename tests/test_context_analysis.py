import pandas as pd

from src.context_analysis import analyze_context, context_stability_score
from src.fingerprint import add_derived_contexts, detect_issues
from src.validation import range_validation


def test_context_analysis_finds_context_missingness(small_sensor_frame):
    frame = small_sensor_frame.copy()
    frame.loc[frame["shift"] == "night", "vibration"] = None
    result = analyze_context(frame, ["shift"], min_group_size=20)
    scores = result.set_index("context_value")["reliability_score"]
    assert scores["night"] < scores["morning"]
    assert result["sufficient_sample"].all()


def test_small_groups_are_flagged():
    frame = pd.DataFrame({"group": ["large"] * 40 + ["tiny"], "value": range(41)})
    result = analyze_context(frame, ["group"], min_group_size=30)
    tiny = result[result["context_value"] == "tiny"].iloc[0]
    assert not bool(tiny["sufficient_sample"])


def test_single_category_has_unavailable_stability():
    frame = pd.DataFrame({"group": ["only"] * 50, "value": range(50)})
    result = analyze_context(frame, ["group"])
    score, _ = context_stability_score(result)
    assert score is None


def test_temperature_and_load_ranges_are_created(small_sensor_frame):
    enriched = add_derived_contexts(small_sensor_frame)
    assert "temperature_range" in enriched
    assert "machine_load_range" in enriched
    assert enriched["temperature_range"].astype(str).eq("normal").all()


def test_context_missing_issues_are_counted(small_sensor_frame):
    frame = small_sensor_frame.copy()
    frame.loc[frame["shift"] == "night", "vibration"] = None
    issues = detect_issues(frame, ["shift"], range_validation(frame), ["record_id"])
    night = issues[(issues["issue_type"] == "context_missing_value") & (issues["context_value"] == "night")]
    assert int(night.iloc[0]["issue_count"]) == 60
