"""CPO Supply Chain Tracker — Streamlit dashboard for crude palm oil traceability."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

DATA_PATH = Path(__file__).parent / "demo" / "sample_data.csv"

RSPO_CHECKLIST_ITEMS: tuple[str, ...] = (
    "No deforestation after November 2005 cut-off date",
    "Free, Prior and Informed Consent (FPIC) obtained",
    "High Conservation Value (HCV) areas identified and protected",
    "High Carbon Stock (HCS) assessment completed",
    "No new planting on peat regardless of depth",
    "Greenhouse gas emissions monitored and reduced",
    "Workers' rights and fair labor conditions ensured",
    "Smallholder inclusion programme in place",
    "Traceability to plantation level documented",
    "Annual surveillance audit completed",
)


@dataclass(frozen=True)
class DataSummary:
    """Immutable summary statistics for the dashboard."""

    total_plantations: int
    total_mills: int
    total_ffb_tonnes: float
    total_cpo_tonnes: float
    avg_extraction_rate: float
    rspo_certified_pct: float
    provinces: tuple[str, ...]


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load and parse sample CSV data with proper types."""
    df = pd.read_csv(
        path,
        parse_dates=["date", "rspo_audit_date", "rspo_next_audit"],
    )
    df = df.assign(
        rspo_certified=df["rspo_certified"].astype(bool),
        smallholder=df["smallholder"].astype(bool),
    )
    return df


def compute_summary(df: pd.DataFrame) -> DataSummary:
    """Derive immutable summary statistics from the dataset."""
    return DataSummary(
        total_plantations=int(df["plantation_id"].nunique()),
        total_mills=int(df["mill_id"].nunique()),
        total_ffb_tonnes=round(df["ffb_yield_kg"].sum() / 1000, 1),
        total_cpo_tonnes=round(df["cpo_yield_kg"].sum() / 1000, 1),
        avg_extraction_rate=round(float(df["extraction_rate_pct"].mean()), 1),
        rspo_certified_pct=round(
            float(df["rspo_certified"].mean()) * 100, 1
        ),
        provinces=tuple(sorted(df["province"].unique())),
    )


def filter_data(
    df: pd.DataFrame,
    *,
    provinces: list[str] | None = None,
    rspo_only: bool = False,
    smallholder_only: bool = False,
) -> pd.DataFrame:
    """Return a filtered copy — never mutates the original."""
    filtered = df.copy()
    if provinces:
        filtered = filtered[filtered["province"].isin(provinces)]
    if rspo_only:
        filtered = filtered[filtered["rspo_certified"]]
    if smallholder_only:
        filtered = filtered[filtered["smallholder"]]
    return filtered


# ---------------------------------------------------------------------------
# Map
# ---------------------------------------------------------------------------


def build_supply_chain_map(df: pd.DataFrame) -> folium.Map:
    """Build a Folium map with plantation markers, mill markers, and routes."""
    center_lat = float(df["latitude"].mean())
    center_lon = float(df["longitude"].mean())
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5, tiles="CartoDB positron")

    plantation_group = folium.FeatureGroup(name="Plantations")
    mill_group = folium.FeatureGroup(name="Mills")
    route_group = folium.FeatureGroup(name="Transport Routes")

    for _, row in df.iterrows():
        color = "green" if row["rspo_certified"] else "red"
        popup_html = (
            f"<b>{row['plantation_name']}</b><br>"
            f"Province: {row['province']}<br>"
            f"FFB Yield: {row['ffb_yield_kg']:,} kg<br>"
            f"RSPO: {'Certified' if row['rspo_certified'] else 'Not Certified'}"
        )
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=7,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=row["plantation_name"],
        ).add_to(plantation_group)

    mills_seen: set[str] = set()
    for _, row in df.iterrows():
        mid = row["mill_id"]
        if mid not in mills_seen:
            mills_seen.add(mid)
            mill_popup = (
                f"<b>{row['mill_name']}</b><br>"
                f"Mill ID: {mid}"
            )
            folium.Marker(
                location=[row["mill_latitude"], row["mill_longitude"]],
                icon=folium.Icon(color="blue", icon="industry", prefix="fa"),
                popup=folium.Popup(mill_popup, max_width=250),
                tooltip=row["mill_name"],
            ).add_to(mill_group)

        folium.PolyLine(
            locations=[
                [row["latitude"], row["longitude"]],
                [row["mill_latitude"], row["mill_longitude"]],
            ],
            color="gray",
            weight=1.5,
            opacity=0.5,
            dash_array="5",
        ).add_to(route_group)

    plantation_group.add_to(m)
    mill_group.add_to(m)
    route_group.add_to(m)
    folium.LayerControl().add_to(m)
    return m


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------


def create_yield_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Monthly FFB and CPO yield trends as an interactive Plotly chart."""
    monthly = (
        df.assign(month=df["date"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False)
        .agg(ffb_tonnes=("ffb_yield_kg", lambda s: round(s.sum() / 1000, 1)),
             cpo_tonnes=("cpo_yield_kg", lambda s: round(s.sum() / 1000, 1)))
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["ffb_tonnes"],
        mode="lines+markers", name="FFB (tonnes)",
        line={"color": "#2E86AB"},
    ))
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["cpo_tonnes"],
        mode="lines+markers", name="CPO (tonnes)",
        line={"color": "#A23B72"},
    ))
    fig.update_layout(
        title="Monthly Yield Trends",
        xaxis_title="Month",
        yaxis_title="Tonnes",
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


def create_extraction_rate_chart(df: pd.DataFrame) -> go.Figure:
    """Extraction rate by mill as a grouped bar chart."""
    mill_stats = (
        df.groupby("mill_name", as_index=False)
        .agg(
            avg_extraction=("extraction_rate_pct", "mean"),
            total_ffb=("ffb_yield_kg", "sum"),
            total_cpo=("cpo_yield_kg", "sum"),
        )
        .assign(avg_extraction=lambda d: d["avg_extraction"].round(1))
    )
    fig = px.bar(
        mill_stats,
        x="mill_name",
        y="avg_extraction",
        color="avg_extraction",
        color_continuous_scale="RdYlGn",
        title="Average Extraction Rate by Mill (%)",
        labels={"mill_name": "Mill", "avg_extraction": "Extraction Rate (%)"},
        text="avg_extraction",
    )
    fig.update_layout(template="plotly_white", showlegend=False)
    fig.update_traces(textposition="outside")
    return fig


def create_province_breakdown_chart(df: pd.DataFrame) -> go.Figure:
    """Sunburst chart: Province -> Plantation -> RSPO status."""
    chart_df = df.assign(
        rspo_status=df["rspo_certified"].map({True: "RSPO Certified", False: "Not Certified"}),
        ffb_tonnes=df["ffb_yield_kg"] / 1000,
    )
    fig = px.sunburst(
        chart_df,
        path=["province", "plantation_name", "rspo_status"],
        values="ffb_tonnes",
        color="rspo_status",
        color_discrete_map={"RSPO Certified": "#27AE60", "Not Certified": "#E74C3C"},
        title="Supply Chain Breakdown by Province",
    )
    fig.update_layout(template="plotly_white")
    return fig


def create_quality_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter plot: moisture content vs FFA percentage, sized by yield."""
    fig = px.scatter(
        df,
        x="moisture_content_pct",
        y="ffa_pct",
        size="ffb_yield_kg",
        color="rspo_certified",
        color_discrete_map={True: "#27AE60", False: "#E74C3C"},
        hover_name="plantation_name",
        title="CPO Quality: Moisture vs FFA",
        labels={
            "moisture_content_pct": "Moisture Content (%)",
            "ffa_pct": "Free Fatty Acid (%)",
            "rspo_certified": "RSPO Certified",
        },
    )
    fig.update_layout(template="plotly_white")
    return fig


def create_transport_chart(df: pd.DataFrame) -> go.Figure:
    """Box plot of transport distances by mode."""
    fig = px.box(
        df,
        x="transport_mode",
        y="transport_distance_km",
        color="transport_mode",
        title="Transport Distance Distribution by Mode",
        labels={
            "transport_mode": "Transport Mode",
            "transport_distance_km": "Distance (km)",
        },
        points="all",
    )
    fig.update_layout(template="plotly_white", showlegend=False)
    return fig


def create_mill_efficiency_table(df: pd.DataFrame) -> pd.DataFrame:
    """Return mill efficiency summary as a new DataFrame."""
    return (
        df.groupby(["mill_id", "mill_name"], as_index=False)
        .agg(
            shipments=("plantation_id", "count"),
            total_ffb_kg=("ffb_yield_kg", "sum"),
            total_cpo_kg=("cpo_yield_kg", "sum"),
            avg_extraction_pct=("extraction_rate_pct", "mean"),
            avg_moisture_pct=("moisture_content_pct", "mean"),
            avg_ffa_pct=("ffa_pct", "mean"),
            certified_suppliers=("rspo_certified", "sum"),
        )
        .assign(
            avg_extraction_pct=lambda d: d["avg_extraction_pct"].round(1),
            avg_moisture_pct=lambda d: d["avg_moisture_pct"].round(1),
            avg_ffa_pct=lambda d: d["avg_ffa_pct"].round(1),
            total_ffb_tonnes=lambda d: (d["total_ffb_kg"] / 1000).round(1),
            total_cpo_tonnes=lambda d: (d["total_cpo_kg"] / 1000).round(1),
        )
        .drop(columns=["total_ffb_kg", "total_cpo_kg"])
    )


# ---------------------------------------------------------------------------
# RSPO Compliance
# ---------------------------------------------------------------------------


def get_rspo_status(df: pd.DataFrame) -> pd.DataFrame:
    """Build RSPO compliance status per plantation."""
    today = date.today()
    rspo_df = (
        df[["plantation_id", "plantation_name", "rspo_certified",
            "rspo_license_number", "rspo_audit_date", "rspo_next_audit"]]
        .drop_duplicates(subset=["plantation_id"])
        .copy()
    )
    rspo_df = rspo_df.assign(
        audit_overdue=rspo_df["rspo_next_audit"].apply(
            lambda d: bool(pd.notna(d) and d.date() < today)
        ),
    )
    return rspo_df


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------


def render_sidebar(df: pd.DataFrame) -> tuple[list[str], bool, bool]:
    """Render sidebar filters and return selections."""
    st.sidebar.title("Filters")
    provinces = st.sidebar.multiselect(
        "Province",
        options=sorted(df["province"].unique()),
        default=[],
    )
    rspo_only = st.sidebar.checkbox("RSPO Certified Only", value=False)
    smallholder_only = st.sidebar.checkbox("Smallholders Only", value=False)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Data:** 25 supply chain records across 6 Indonesian provinces."
    )
    return provinces, rspo_only, smallholder_only


def render_kpi_row(summary: DataSummary) -> None:
    """Display top-level KPI metric cards."""
    cols = st.columns(6)
    cols[0].metric("Plantations", summary.total_plantations)
    cols[1].metric("Mills", summary.total_mills)
    cols[2].metric("FFB (t)", f"{summary.total_ffb_tonnes:,.1f}")
    cols[3].metric("CPO (t)", f"{summary.total_cpo_tonnes:,.1f}")
    cols[4].metric("Avg OER", f"{summary.avg_extraction_rate}%")
    cols[5].metric("RSPO %", f"{summary.rspo_certified_pct}%")


def render_map_tab(df: pd.DataFrame) -> None:
    """Render the interactive supply chain map."""
    st.subheader("Supply Chain Map")
    st.caption("Green = RSPO Certified | Red = Not Certified | Blue = Mill")
    supply_map = build_supply_chain_map(df)
    st_folium(supply_map, width=900, height=500, returned_objects=[])


def render_yield_tab(df: pd.DataFrame) -> None:
    """Render yield analysis charts."""
    st.subheader("Yield Analysis")
    st.plotly_chart(create_yield_trend_chart(df), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_province_breakdown_chart(df), use_container_width=True)
    with col2:
        st.plotly_chart(create_quality_scatter(df), use_container_width=True)


def render_mill_tab(df: pd.DataFrame) -> None:
    """Render mill processing efficiency dashboard."""
    st.subheader("Mill Processing Efficiency")
    st.plotly_chart(create_extraction_rate_chart(df), use_container_width=True)

    efficiency = create_mill_efficiency_table(df)
    st.dataframe(efficiency, use_container_width=True, hide_index=True)

    st.plotly_chart(create_transport_chart(df), use_container_width=True)


def render_rspo_tab(df: pd.DataFrame) -> None:
    """Render RSPO compliance checklist and status."""
    st.subheader("RSPO Compliance Tracker")

    rspo_status = get_rspo_status(df)

    certified_count = int(rspo_status["rspo_certified"].sum())
    total_count = len(rspo_status)
    st.progress(
        certified_count / total_count,
        text=f"{certified_count}/{total_count} plantations RSPO certified",
    )

    overdue = rspo_status[rspo_status["audit_overdue"]]
    if not overdue.empty:
        st.warning(
            f"{len(overdue)} plantation(s) have overdue RSPO audits.",
            icon="\u26a0\ufe0f",
        )

    st.markdown("#### RSPO Principles & Criteria Checklist")
    checklist_state: dict[str, bool] = {}
    for item in RSPO_CHECKLIST_ITEMS:
        checklist_state[item] = st.checkbox(item, value=False, key=f"rspo_{item}")

    completed = sum(checklist_state.values())
    st.info(f"Checklist progress: {completed}/{len(RSPO_CHECKLIST_ITEMS)} items checked")

    st.markdown("#### Plantation Certification Status")
    display_cols = [
        "plantation_id", "plantation_name", "rspo_certified",
        "rspo_license_number", "rspo_audit_date", "rspo_next_audit", "audit_overdue",
    ]
    st.dataframe(rspo_status[display_cols], use_container_width=True, hide_index=True)


def render_data_tab(df: pd.DataFrame) -> None:
    """Render raw data explorer."""
    st.subheader("Raw Data Explorer")
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="cpo_supply_chain_data.csv",
        mime="text/csv",
    )


def main() -> None:
    """Entry point for the Streamlit app."""
    st.set_page_config(
        page_title="CPO Supply Chain Tracker",
        page_icon="\U0001f334",
        layout="wide",
    )
    st.title("\U0001f334 CPO Supply Chain Tracker")
    st.markdown("Plantation-to-mill traceability, RSPO compliance, and yield analysis.")

    raw_df = load_data()
    provinces, rspo_only, smallholder_only = render_sidebar(raw_df)

    df = filter_data(
        raw_df,
        provinces=provinces,
        rspo_only=rspo_only,
        smallholder_only=smallholder_only,
    )

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    summary = compute_summary(df)
    render_kpi_row(summary)

    tab_map, tab_yield, tab_mill, tab_rspo, tab_data = st.tabs(
        ["Supply Chain Map", "Yield Analysis", "Mill Efficiency", "RSPO Compliance", "Raw Data"]
    )
    with tab_map:
        render_map_tab(df)
    with tab_yield:
        render_yield_tab(df)
    with tab_mill:
        render_mill_tab(df)
    with tab_rspo:
        render_rspo_tab(df)
    with tab_data:
        render_data_tab(df)


if __name__ == "__main__":
    main()
