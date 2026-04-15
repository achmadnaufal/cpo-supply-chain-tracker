# CPO Supply Chain Tracker — Dashboard Views

This document describes all pages and views available in the application.

## Overview / KPI Row

The top of the dashboard displays six key performance indicator cards:
- **Plantations** — Total unique plantation sources
- **Mills** — Total processing mills
- **FFB (t)** — Total Fresh Fruit Bunch yield in tonnes
- **CPO (t)** — Total Crude Palm Oil output in tonnes
- **Avg OER** — Average Oil Extraction Rate percentage
- **RSPO %** — Percentage of RSPO-certified plantations

## Sidebar Filters

All views respond to global filters in the sidebar:
- **Province** — Multi-select dropdown for Indonesian provinces
- **RSPO Certified Only** — Toggle to show only certified plantations
- **Smallholders Only** — Toggle to show only smallholder plantations

## Tab 1: Supply Chain Map

Interactive Folium map centered on Indonesia showing:
- **Green circles** — RSPO-certified plantations
- **Red circles** — Non-certified plantations
- **Blue markers** — Processing mills (with industry icon)
- **Gray dashed lines** — Transport routes from plantation to mill
- **Layer control** — Toggle plantations, mills, and routes independently
- **Popups** — Click any marker for details (name, province, yield, certification status)

## Tab 2: Yield Analysis

Three interactive Plotly charts:
1. **Monthly Yield Trends** — Dual-line chart tracking FFB and CPO production over time with hover details
2. **Province Breakdown** — Sunburst chart showing Province > Plantation > RSPO Status hierarchy sized by FFB volume
3. **CPO Quality Scatter** — Bubble chart plotting moisture content vs free fatty acid percentage, sized by yield and colored by RSPO status

## Tab 3: Mill Efficiency

Three components:
1. **Extraction Rate Bar Chart** — Color-gradient bar chart comparing average OER across mills
2. **Efficiency Summary Table** — Detailed table per mill showing shipment count, total FFB/CPO tonnes, average extraction rate, moisture, FFA, and certified supplier count
3. **Transport Distance Box Plot** — Distribution of transport distances by mode (truck vs barge) with individual data points

## Tab 4: RSPO Compliance

Four components:
1. **Progress Bar** — Visual indicator of certified vs total plantations
2. **Overdue Alert** — Warning banner when any plantation has an overdue RSPO audit
3. **Compliance Checklist** — Interactive checklist of 10 RSPO Principles & Criteria items with progress counter
4. **Certification Status Table** — Per-plantation table showing certification status, license number, last audit date, next audit date, and overdue flag

## Tab 5: Raw Data

- **Full Data Table** — Scrollable, sortable table of all supply chain records
- **CSV Download** — Button to download the current filtered dataset as CSV
