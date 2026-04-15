"""Tests for RSPO compliance functions."""

from __future__ import annotations

import pandas as pd

from app import get_rspo_status, RSPO_CHECKLIST_ITEMS, create_mill_efficiency_table


class TestGetRspoStatus:
    """Tests for get_rspo_status."""

    def test_returns_dataframe(self, small_df: pd.DataFrame) -> None:
        result = get_rspo_status(small_df)
        assert isinstance(result, pd.DataFrame)

    def test_unique_plantations(self, small_df: pd.DataFrame) -> None:
        result = get_rspo_status(small_df)
        assert result["plantation_id"].is_unique

    def test_has_audit_overdue_column(self, small_df: pd.DataFrame) -> None:
        result = get_rspo_status(small_df)
        assert "audit_overdue" in result.columns

    def test_non_certified_not_overdue(self, small_df: pd.DataFrame) -> None:
        result = get_rspo_status(small_df)
        non_certified = result[~result["rspo_certified"]]
        assert not non_certified["audit_overdue"].any()

    def test_preserves_license_numbers(self, small_df: pd.DataFrame) -> None:
        result = get_rspo_status(small_df)
        certified = result[result["rspo_certified"]]
        assert certified["rspo_license_number"].notna().all()


class TestRspoChecklist:
    """Tests for RSPO checklist items."""

    def test_has_items(self) -> None:
        assert len(RSPO_CHECKLIST_ITEMS) > 0

    def test_items_are_strings(self) -> None:
        assert all(isinstance(item, str) for item in RSPO_CHECKLIST_ITEMS)

    def test_items_are_unique(self) -> None:
        assert len(RSPO_CHECKLIST_ITEMS) == len(set(RSPO_CHECKLIST_ITEMS))

    def test_checklist_is_immutable(self) -> None:
        assert isinstance(RSPO_CHECKLIST_ITEMS, tuple)


class TestMillEfficiencyTable:
    """Tests for create_mill_efficiency_table."""

    def test_returns_dataframe(self, small_df: pd.DataFrame) -> None:
        result = create_mill_efficiency_table(small_df)
        assert isinstance(result, pd.DataFrame)

    def test_groups_by_mill(self, small_df: pd.DataFrame) -> None:
        result = create_mill_efficiency_table(small_df)
        assert len(result) == 2  # M001, M002

    def test_has_efficiency_columns(self, small_df: pd.DataFrame) -> None:
        result = create_mill_efficiency_table(small_df)
        assert "avg_extraction_pct" in result.columns
        assert "total_ffb_tonnes" in result.columns
        assert "total_cpo_tonnes" in result.columns
