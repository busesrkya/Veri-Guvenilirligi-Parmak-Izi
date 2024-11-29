from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def small_sensor_frame() -> pd.DataFrame:
    rows = 120
    return pd.DataFrame(
        {
            "record_id": range(rows),
            "timestamp": pd.date_range("2025-01-01", periods=rows, freq="h"),
            "machine_id": ["M01"] * 60 + ["M02"] * 60,
            "sensor_id": ["S01"] * 60 + ["S02"] * 60,
            "shift": (["morning"] * 30 + ["night"] * 30) * 2,
            "temperature": [50.0] * rows,
            "pressure": [5.0] * rows,
            "vibration": [3.0] * rows,
            "humidity": [50.0] * rows,
            "operating_speed": [2000.0] * rows,
            "machine_load": [60.0] * rows,
            "operating_status": ["normal"] * rows,
            "quality_label": ["normal", "attention"] * 60,
        }
    )
