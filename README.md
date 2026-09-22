# Salmon Run Contest Report Generator

This repo contains programs designed to process Cabrillo log files from the **Salmon Run Amateur Radio Contest** and generate a self-contained HTML report. 

The generated report features rate charts, geographic choropleth heatmaps (Washington Counties, US States, and Canadian Provinces), multiplier breakdowns, and automated executive summary analytics.


## Local Python script: `generate_report.py`

A Python script which takes a Cabrillo file as input and outputs the report.

You can see a sample from my 2026 Salmon Run participation at https://jeffschoner.github.io/salmon-run-analyzer/ka7w.html

## Embedded HTML/JavaScript: `docs/index.html`

After I used Gemini to help write the Python script, it occurred to me
that this could just be a single page HTML/JavaScript application where you
can upload the Cabrillo file and process it in the browser. This file is
located in docs/index.html. It can be accessed at https://jeffschoner.github.io/salmon-run-analyzer.

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

## Prerequisites for Python script

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
python generate_report.py <path_to_your_cabrillo_file.log>
```

Output will be in `salmon_run_2026_report.html`
