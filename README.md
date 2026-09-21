# Salmon Run Contest Report Generator

A Python script designed to process Cabrillo log files from the **Salmon Run Amateur Radio Contest** and generate an interactive, self-contained HTML report. 

The generated report features dynamic rate charts, geographic choropleth heatmaps (Washington Counties, US States, and Canadian Provinces), multiplier breakdowns, and automated executive summary analytics.

You can see a sample at https://jeffschoner.github.io/salmon-run-analyzer/ka7w.html

---

## Features

- **Automated Performance Analytics:** Dynamically calculates peak QSO rates, dominant bands/modes, active operating hours, and multiplier progress.
- **Interactive Rate Graphs:** Stacked hourly bar charts powered by [Plotly](https://plotly.com/python/) to analyze band and mode (CW vs. Phone) progression.
- **Geographic Choropleth Heatmaps:**
  - Washington State Counties
  - United States
  - Canadian Provinces & Territories
- **Standardized Band Coloring:** Band charts utilize standard PSKReporter color palettes for rapid visual identification.
- **Detailed Data Breakdown Tables:**
  - Washington Counties
  - US States
  - Canadian Provinces
  - DX & Other Contacts

---

## Prerequisites

- **Python 3.8+**
- An active internet connection (used when running the script to fetch official US County and Canadian Province GeoJSON boundary files).

---

## Environment Setup

It is recommended to run this project inside a Python virtual environment to manage dependencies cleanly.

### MacOS/Linux

```
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all required packages at once
pip install -r requirements.txt
```

### Windows

```
:: Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

:: Install all required packages at once
pip install -r requirements.txt
```

## Run

```
python generate_report_3.py <path_to_your_cabrillo_file.log>
```

Output will be in `salmon_run_2026_report.html`
