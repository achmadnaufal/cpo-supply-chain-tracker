# CPO Supply Chain Tracker

[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-30%2B%20passing-brightgreen)](tests/)

Interactive Streamlit dashboard for tracking crude palm oil (CPO) supply chains from plantation to mill. Provides RSPO compliance monitoring, yield trend analysis, and mill processing efficiency metrics across Indonesian provinces.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
pytest tests/
```

## Features

- **Interactive Supply Chain Map** — Folium map showing plantation locations (color-coded by RSPO status), mill destinations, and transport routes with layer controls
- **Yield Trend Analysis** — Monthly FFB and CPO yield trends, province breakdown sunburst chart, and CPO quality scatter plots (Plotly)
- **Mill Processing Efficiency** — Extraction rate comparison across mills, efficiency summary table, and transport distance distribution
- **RSPO Compliance Tracker** — Certification status per plantation, audit overdue detection, and interactive compliance checklist based on RSPO Principles & Criteria
- **Raw Data Explorer** — Filterable data table with CSV download capability

## Sample Output

The dashboard includes 25 records across 6 Indonesian provinces (Riau, North Sumatra, West Kalimantan, Central Kalimantan, South Sumatra, Jambi) covering:
- FFB yields from 18,200 kg to 35,100 kg per shipment
- Extraction rates between 19% and 23%
- Both truck and barge transport modes
- Mix of RSPO-certified and non-certified plantations
- Smallholder and estate plantations

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Data | Pandas |
| Charts | Plotly |
| Maps | Folium + streamlit-folium |
| Testing | pytest |

## Project Structure

```
cpo-supply-chain-tracker/
├── app.py                  # Main Streamlit application
├── demo/
│   └── sample_data.csv     # 25 rows of realistic Indonesian CPO data
├── tests/
│   ├── conftest.py         # Shared test fixtures
│   ├── test_data_loading.py
│   ├── test_data_processing.py
│   ├── test_charts.py
│   ├── test_map.py
│   └── test_rspo.py
├── docs/
│   └── SCREENSHOTS.md      # Documentation of all dashboard views
├── requirements.txt
├── LICENSE
└── README.md
```
