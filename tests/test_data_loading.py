"""Tests for data loading and parsing."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from app import load_data


class TestLoadData:
    """Tests for the load_data function."""

    def test_loads_csv_successfully(self, sample_data_path: Path) -> None:
        df = load_data(sample_data_path)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_has_expected_row_count(self, sample_data_path: Path) -> None:
        df = load_data(sample_data_path)
        assert len(df) == 25

    def test_has_required_columns(self, sample_data_path: Path) -> None:
        df = load_data(sample_data_path)
        required = {
            "plantation_id", "plantation_name", "province",
            "latitude", "longitude", "mill_id", "mill_name",
            "ffb_yield_kg", "cpo_yield_kg", "extraction_rate_pct",
            "rspo_certified", "date",
        }
        assert required.issubset(set(df.columns))

    def test_date_column_is_datetime(self, sample_data_path: Path) -> None:
        df = load_data(sample_data_path)
        assert pd.api.types.is_datetime64_any_dtype(df["date"])

    def test_rspo_certified_is_bool(self, sample_data_path: Path) -> None:
        df = load_data(sample_data_path)
        assert df["rspo_certified"].dtype == bool

    def test_smallholder_is_bool(self, sample_data_path: Path) -> None:
        df = load_data(sample_data_path)
        assert df["smallholder"].dtype == bool

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_data(tmp_path / "nonexistent.csv")

    def test_yields_are_positive(self, sample_df: pd.DataFrame) -> None:
        assert (sample_df["ffb_yield_kg"] > 0).all()
        assert (sample_df["cpo_yield_kg"] > 0).all()
