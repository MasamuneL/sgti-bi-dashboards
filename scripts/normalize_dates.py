"""Date/time normalization utilities for the SGTI CSV -> Parquet pipeline.

All upstream timestamps are ISO-8601 with UTC ("2026-07-04T20:32:38.000Z").
Date-only columns are stored as UTC midnight ("2026-01-19T06:00:00.000Z"),
which corresponds to 00:00 local (UTC-6). This module centralizes the
parsing rules so every table is normalized consistently.
"""

from __future__ import annotations

import pandas as pd


def parse_date_series(series: pd.Series) -> pd.Series:
    """Parse a date-only column to a Python ``datetime.date`` object series.

    ``2026-01-19T06:00:00.000Z`` -> ``datetime.date(2026, 1, 19)``.
    Unparseable values become ``None``.
    """
    parsed = pd.to_datetime(series, errors="coerce", format="ISO8601", utc=True)
    return pd.Series(
        [d.date() if pd.notna(d) else None for d in parsed],
        index=series.index,
        dtype="object",
    )


def parse_datetime_series(series: pd.Series) -> pd.Series:
    """Parse a datetime column to a timezone-aware UTC pandas datetime series.

    Values keep their UTC offset normalization (``.000Z`` suffix dropped).
    """
    return pd.to_datetime(series, errors="coerce", format="ISO8601", utc=True)


def normalize_time_series(series: pd.Series) -> pd.Series:
    """Normalize HH:MM / HH:MM:SS time strings to a padded HH:MM:SS form.

    e.g. ``"18:17"`` -> ``"18:17:00"``, ``"07:00:00"`` stays unchanged.
    Empty values become ``None``.
    """

    def _norm(value):
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        parts = text.split(":")
        if len(parts) == 2:
            return f"{text}:00"
        return text

    return series.map(_norm)


def clean_string_series(series: pd.Series) -> pd.Series:
    """Strip surrounding whitespace; convert empty strings to None."""
    cleaned = series.replace({pd.NA: None, "": None})
    return cleaned.map(lambda v: v.strip() if isinstance(v, str) else v)