"""Tests for chart creation functions."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from app import (
    create_extraction_rate_chart,
    create_province_breakdown_chart,
    create_quality_scatter,
    create_transport_chart,
    create_yield_trend_chart,
)


class TestYieldTrendChart:
    """Tests for create_yield_trend_chart."""

    def test_returns_figure(self, small_df: pd.DataFrame) -> None:
        fig = create_yield_trend_chart(small_df)
        assert isinstance(fig, go.Figure)

    def test_has_two_traces(self, small_df: pd.DataFrame) -> None:
        fig = create_yield_trend_chart(small_df)
        assert len(fig.data) == 2

    def test_trace_names(self, small_df: pd.DataFrame) -> None:
        fig = create_yield_trend_chart(small_df)
        names = {t.name for t in fig.data}
        assert "FFB (tonnes)" in names
        assert "CPO (tonnes)" in names


class TestExtractionRateChart:
    """Tests for create_extraction_rate_chart."""

    def test_returns_figure(self, small_df: pd.DataFrame) -> None:
        fig = create_extraction_rate_chart(small_df)
        assert isinstance(fig, go.Figure)

    def test_has_data(self, small_df: pd.DataFrame) -> None:
        fig = create_extraction_rate_chart(small_df)
        assert len(fig.data) > 0


class TestProvinceBreakdownChart:
    """Tests for create_province_breakdown_chart."""

    def test_returns_figure(self, small_df: pd.DataFrame) -> None:
        fig = create_province_breakdown_chart(small_df)
        assert isinstance(fig, go.Figure)


class TestQualityScatter:
    """Tests for create_quality_scatter."""

    def test_returns_figure(self, small_df: pd.DataFrame) -> None:
        fig = create_quality_scatter(small_df)
        assert isinstance(fig, go.Figure)

    def test_has_data_points(self, small_df: pd.DataFrame) -> None:
        fig = create_quality_scatter(small_df)
        assert len(fig.data) > 0


class TestTransportChart:
    """Tests for create_transport_chart."""

    def test_returns_figure(self, small_df: pd.DataFrame) -> None:
        fig = create_transport_chart(small_df)
        assert isinstance(fig, go.Figure)
