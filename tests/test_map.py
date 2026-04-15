"""Tests for map building functionality."""

from __future__ import annotations

import folium
import pandas as pd

from app import build_supply_chain_map


class TestBuildSupplyChainMap:
    """Tests for build_supply_chain_map."""

    def test_returns_folium_map(self, small_df: pd.DataFrame) -> None:
        m = build_supply_chain_map(small_df)
        assert isinstance(m, folium.Map)

    def test_map_has_children(self, small_df: pd.DataFrame) -> None:
        m = build_supply_chain_map(small_df)
        children = list(m._children.values())
        assert len(children) > 0

    def test_map_renders_html(self, small_df: pd.DataFrame) -> None:
        m = build_supply_chain_map(small_df)
        html = m._repr_html_()
        assert isinstance(html, str)
        assert len(html) > 0

    def test_map_contains_plantation_names(self, small_df: pd.DataFrame) -> None:
        m = build_supply_chain_map(small_df)
        html = m._repr_html_()
        assert "Farm A" in html or "Farm B" in html
