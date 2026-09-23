# Salmon Run Contest Report Generator

This repo contains programs designed to process Cabrillo log files from the **Salmon Run Amateur Radio Contest** and generate a self-contained HTML report. 

The generated report features rate charts, geographic choropleth heatmaps (Washington Counties, US States, and Canadian Provinces), multiplier breakdowns, and automated executive summary analytics.

You can see a sample from my 2026 Salmon Run participation at https://jeffschoner.github.io/salmon-run-analyzer/ka7w.html

This is a single page HTML/JavaScript application where you
can upload the Cabrillo file and process it in the browser. This file is
located in docs/index.html. It can be accessed at https://jeffschoner.github.io/salmon-run-analyzer.

---

## Features

- **Automated Performance Analytics:** Dynamically calculates peak QSO rates, dominant bands/modes, active operating hours, and multiplier progress.
- **Interactive Rate Graphs:** Stacked hourly bar charts powered by [Plotly](https://plotly.com/python/) to analyze band and mode (CW vs. Phone) progression.
- **Geographic Choropleth Heatmaps:**
  - Washington State Counties
  - United States and Canadian Provinces & Territories
- **Standardized Band Coloring:** Band charts utilize standard PSKReporter color palettes for rapid visual identification.
- **Detailed Data Breakdown Tables:**
  - Washington Counties
  - US States
  - Canadian Provinces
  - DX & Other Contacts

