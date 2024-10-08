from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_csv(path_or_buffer, timestamp_column: str | None = "timestamp") -> pd.DataFrame:
    frame = pd.read_csv(path_or_buffer)
    if timestamp_column and timestamp_column in frame.columns:
        frame[timestamp_column] = pd.to_datetime(frame[timestamp_column], errors="coerce")
    return frame


def save_csv(frame: pd.DataFrame, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False)
