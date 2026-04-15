"""Tests for data processing and summary computation."""

from __future__ import annotations

import pandas as pd
import pytest

from app import compute_summary, filter_data, DataSummary


class TestComputeSummary:
    """Tests for compute_summary."""

    def test_returns_data_summary(self, small_df: pd.DataFrame) -> None:
        result = compute_summary(small_df)
        assert isinstance(result, DataSummary)

    def test_counts_unique_plantations(self, small_df: pd.DataFrame) -> None:
        result = compute_summary(small_df)
        assert result.total_plantations == 3

    def test_counts_unique_mills(self, small_df: pd.DataFrame) -> None:
        result = compute_summary(small_df)
        assert result.total_mills == 2

    def test_ffb_tonnes_conversion(self, small_df: pd.DataFrame) -> None:
        expected = round((28000 + 32000 + 20000) / 1000, 1)
        result = compute_summary(small_df)
        assert result.total_ffb_tonnes == expected

    def test_cpo_tonnes_conversion(self, small_df: pd.DataFrame) -> None:
        expected = round((6160 + 7360 + 4200) / 1000, 1)
        result = compute_summary(small_df)
        assert result.total_cpo_tonnes == expected

    def test_avg_extraction_rate(self, small_df: pd.DataFrame) -> None:
        result = compute_summary(small_df)
        assert result.avg_extraction_rate == 22.0

    def test_rspo_pct(self, small_df: pd.DataFrame) -> None:
        result = compute_summary(small_df)
        assert result.rspo_certified_pct == pytest.approx(66.7, abs=0.1)

    def test_provinces_sorted(self, small_df: pd.DataFrame) -> None:
        result = compute_summary(small_df)
        assert result.provinces == ("North Sumatra", "Riau")

    def test_summary_is_immutable(self, small_df: pd.DataFrame) -> None:
        result = compute_summary(small_df)
        with pytest.raises(AttributeError):
            result.total_plantations = 999  # type: ignore[misc]


class TestFilterData:
    """Tests for filter_data."""

    def test_no_filters_returns_all(self, small_df: pd.DataFrame) -> None:
        result = filter_data(small_df)
        assert len(result) == len(small_df)

    def test_province_filter(self, small_df: pd.DataFrame) -> None:
        result = filter_data(small_df, provinces=["Riau"])
        assert len(result) == 2
        assert (result["province"] == "Riau").all()

    def test_rspo_filter(self, small_df: pd.DataFrame) -> None:
        result = filter_data(small_df, rspo_only=True)
        assert len(result) == 2
        assert result["rspo_certified"].all()

    def test_smallholder_filter(self, small_df: pd.DataFrame) -> None:
        result = filter_data(small_df, smallholder_only=True)
        assert len(result) == 1
        assert result["smallholder"].all()

    def test_combined_filters(self, small_df: pd.DataFrame) -> None:
        result = filter_data(small_df, provinces=["Riau"], rspo_only=True)
        assert len(result) == 2

    def test_filter_does_not_mutate_original(self, small_df: pd.DataFrame) -> None:
        original_len = len(small_df)
        _ = filter_data(small_df, rspo_only=True)
        assert len(small_df) == original_len

    def test_empty_province_list_returns_all(self, small_df: pd.DataFrame) -> None:
        result = filter_data(small_df, provinces=[])
        assert len(result) == len(small_df)
