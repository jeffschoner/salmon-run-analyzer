## Local Python script: `generate_report.py`

A Python script which takes a Cabrillo file as input and outputs the report. This doesn't have all the latest changes, but is preserved for posterity in `old-python`.

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
