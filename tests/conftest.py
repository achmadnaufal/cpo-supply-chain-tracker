"""Shared fixtures for CPO Supply Chain Tracker tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_data_path() -> Path:
    """Path to the sample CSV file."""
    return Path(__file__).parent.parent / "demo" / "sample_data.csv"


@pytest.fixture
def sample_df(sample_data_path: Path) -> pd.DataFrame:
    """Loaded sample DataFrame."""
    from app import load_data

    return load_data(sample_data_path)


@pytest.fixture
def small_df() -> pd.DataFrame:
    """Minimal 3-row DataFrame for isolated tests."""
    return pd.DataFrame({
        "plantation_id": ["P001", "P002", "P003"],
        "plantation_name": ["Farm A", "Farm B", "Farm C"],
        "province": ["Riau", "Riau", "North Sumatra"],
        "latitude": [1.0, 0.8, 2.9],
        "longitude": [102.0, 101.7, 99.0],
        "mill_id": ["M001", "M001", "M002"],
        "mill_name": ["Mill X", "Mill X", "Mill Y"],
        "mill_latitude": [1.6, 1.6, 3.5],
        "mill_longitude": [101.4, 101.4, 98.6],
        "date": pd.to_datetime(["2025-01-15", "2025-02-15", "2025-03-15"]),
        "ffb_yield_kg": [28000, 32000, 20000],
        "cpo_yield_kg": [6160, 7360, 4200],
        "extraction_rate_pct": [22.0, 23.0, 21.0],
        "rspo_certified": [True, True, False],
        "rspo_license_number": ["RSPO-001", "RSPO-002", None],
        "rspo_audit_date": pd.to_datetime(["2024-06-01", "2024-07-01", pd.NaT]),
        "rspo_next_audit": pd.to_datetime(["2025-06-01", "2025-07-01", pd.NaT]),
        "smallholder": [False, False, True],
        "transport_mode": ["truck", "truck", "barge"],
        "transport_distance_km": [85.0, 112.0, 72.0],
        "moisture_content_pct": [18.2, 17.8, 19.1],
        "ffa_pct": [3.1, 2.9, 3.4],
    })
