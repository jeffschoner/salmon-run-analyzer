import sys
import re
from datetime import datetime
from collections import defaultdict
import json
import urllib.request
import pandas as pd
import plotly.graph_objects as go

# --- Reference Data ---

WA_COUNTIES_FIPS = {
    "ADA": ("Adams", "53001"), "ASO": ("Asotin", "53003"), "BEN": ("Benton", "53005"), 
    "CHE": ("Chelan", "53007"), "CLAL": ("Clallam", "53009"), "CLAR": ("Clark", "53011"), 
    "COL": ("Columbia", "53013"), "COW": ("Cowlitz", "53015"), "DOU": ("Douglas", "53017"), 
    "FER": ("Ferry", "53019"), "FRA": ("Franklin", "53021"), "GAR": ("Garfield", "53023"), 
    "GRAN": ("Grant", "53025"), "GRAY": ("Grays Harbor", "53027"), "ISL": ("Island", "53029"), 
    "JEFF": ("Jefferson", "53031"), "KING": ("King", "53033"), "KITS": ("Kitsap", "53035"), 
    "KITT": ("Kittitas", "53037"), "KLI": ("Klickitat", "53039"), "LEW": ("Lewis", "53041"), 
    "LIN": ("Lincoln", "53043"), "MAS": ("Mason", "53045"), "OKA": ("Okanogan", "53047"), 
    "PAC": ("Pacific", "53049"), "PEND": ("Pend Oreille", "53051"), "PIE": ("Pierce", "53053"), 
    "SAN": ("San Juan", "53055"), "SKAG": ("Skagit", "53057"), "SKAM": ("Skamania", "53059"), 
    "SNO": ("Snohomish", "53061"), "SPO": ("Spokane", "53063"), "STE": ("Stevens", "53065"), 
    "THU": ("Thurston", "53067"), "WAH": ("Wahkiakum", "53069"), "WAL": ("Walla Walla", "53071"), 
    "WHA": ("Whatcom", "53073"), "WHI": ("Whitman", "53075"), "YAK": ("Yakima", "53077")
}

WA_COUNTIES = {k: v[0] for k, v in WA_COUNTIES_FIPS.items()}

CANADIAN_PROVINCES = {
    "AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba", "NB": "New Brunswick",
    "NL": "Newfoundland and Labrador", "NS": "Nova Scotia", "NT": "Northwest Territories",
    "NU": "Nunavut", "ON": "Ontario", "PE": "Prince Edward Island", "QC": "Quebec",
    "SK": "Saskatchewan", "YT": "Yukon"
}

US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"
}

# --- GeoJSON Data Loading ---

COUNTIES_GEOJSON_URL = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
try:
    with urllib.request.urlopen(COUNTIES_GEOJSON_URL) as response:
        COUNTIES_GEOJSON = json.loads(response.read().decode())
except Exception as e:
    print(f"Warning: Could not load US Counties GeoJSON: {e}")
    COUNTIES_GEOJSON = None

CANADA_GEOJSON_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/canada.geojson"
try:
    with urllib.request.urlopen(CANADA_GEOJSON_URL) as response:
        CANADA_GEOJSON = json.loads(response.read().decode())
except Exception as e:
    print(f"Warning: Could not load Canada GeoJSON: {e}")
    CANADA_GEOJSON = None

def freq_to_band(freq_str):
    try:
        freq = float(freq_str)
        if 1800 <= freq <= 2000: return "160m"
        elif 3500 <= freq <= 4000: return "80m"
        elif 7000 <= freq <= 7300: return "40m"
        elif 14000 <= freq <= 14350: return "20m"
        elif 21000 <= freq <= 21450: return "15m"
        elif 28000 <= freq <= 29700: return "10m"
        elif 50000 <= freq <= 54000: return "6m"
    except ValueError:
        pass
    return "Other"

def parse_cabrillo(file_path):
    qsos = []
    header_info = {}
    my_locations = set()
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("QSO:"):
                parts = line.split()
                if len(parts) >= 11:
                    freq = parts[1]
                    mode = "CW" if parts[2].upper() == "CW" else "PH"
                    date_str = parts[3]
                    time_str = parts[4]
                    my_call = parts[5]
                    my_rst = parts[6]
                    my_loc = parts[7].upper()
                    ur_call = parts[8]
                    ur_rst = parts[9]
                    ur_loc = parts[10].upper()

                    my_locations.add(my_loc)
                    band = freq_to_band(freq)
                    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H%M")
                    
                    loc_type = "DX"
                    if ur_loc in WA_COUNTIES:
                        loc_type = "WA_COUNTY"
                    elif ur_loc in CANADIAN_PROVINCES:
                        loc_type = "VE_PROV"
                    elif ur_loc in US_STATES:
                        loc_type = "US_STATE"
                    
                    qsos.append({
                        'freq': freq, 'band': band, 'mode': mode,
                        'datetime': dt, 'time_bin': dt.strftime("%Y-%m-%d %H:00"),
                        'my_call': my_call, 'my_loc': my_loc,
                        'ur_call': ur_call, 'ur_loc': ur_loc,
                        'loc_type': loc_type
                    })
            elif ":" in line:
                key, val = line.split(":", 1)
                header_info[key.strip()] = val.strip()

    header_info['OPERATING_LOCATIONS'] = ", ".join(sorted(my_locations)) if my_locations else "Unknown"
    return header_info, qsos

def process_log_data(qsos):
    county_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    state_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    prov_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    dx_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    time_bins_mode = defaultdict(lambda: {"CW": 0, "PH": 0})
    time_bins_band = defaultdict(lambda: defaultdict(int))
    band_totals = defaultdict(int)
    mode_totals = defaultdict(int)
    
    used_bands_set = set()
    mults_worked = set()
    total_qso_points = 0
    w7dx_bonus_modes = set()

    for q in qsos:
        b = q['band']
        m = q['mode']
        loc = q['ur_loc']
        
        used_bands_set.add(b)
        band_totals[b] += 1
        mode_totals[m] += 1
        pts = 3 if m == "CW" else 2
        total_qso_points += pts

        if q['ur_call'].upper() == "W7DX":
            w7dx_bonus_modes.add(m)

        if q['loc_type'] == "WA_COUNTY":
            county_counts[loc][b][m] += 1
            mults_worked.add(loc)
        elif q['loc_type'] == "US_STATE":
            state_counts[loc][b][m] += 1
            mults_worked.add(loc)
        elif q['loc_type'] == "VE_PROV":
            prov_counts[loc][b][m] += 1
            mults_worked.add(loc)
        else:
            dx_counts[loc][b][m] += 1
                
        time_bins_mode[q['time_bin']][m] += 1
        time_bins_band[q['time_bin']][b] += 1

    bonus_points = len(w7dx_bonus_modes) * 500
    final_score = (total_qso_points * len(mults_worked)) + bonus_points

    standard_band_order = ["160m", "80m", "40m", "20m", "15m", "10m", "6m"]
    active_bands = [b for b in standard_band_order if b in used_bands_set]

    return {
        'county_counts': county_counts,
        'state_counts': state_counts,
        'prov_counts': prov_counts,
        'dx_counts': dx_counts,
        'time_bins_mode': time_bins_mode,
        'time_bins_band': time_bins_band,
        'band_totals': band_totals,
        'mode_totals': mode_totals,
        'total_qsos': len(qsos),
        'qso_points': total_qso_points,
        'multipliers': len(mults_worked),
        'bonus_points': bonus_points,
        'final_score': final_score,
        'active_bands': active_bands
    }

def generate_summary_text(data):
    sorted_hours = sorted(data['time_bins_mode'].keys())
    if not sorted_hours:
        return "No QSO data available to build summary."
    
    start_time = sorted_hours[0]
    end_time = sorted_hours[-1]
    total_hours = len(sorted_hours)
    
    peak_hour = None
    peak_count = 0
    for h in sorted_hours:
        count = data['time_bins_mode'][h]['CW'] + data['time_bins_mode'][h]['PH']
        if count > peak_count:
            peak_count = count
            peak_hour = h

    top_band = max(data['band_totals'], key=data['band_totals'].get) if data['band_totals'] else "N/A"
    top_mode = max(data['mode_totals'], key=data['mode_totals'].get) if data['mode_totals'] else "N/A"
    
    return f"""
    <p>Operation spanned <strong>{total_hours} active hours</strong> from <strong>{start_time} UTC</strong> through <strong>{end_time} UTC</strong>, logging a total of <strong>{data['total_qsos']} contacts</strong>.</p>
    <ul>
        <li><strong>Peak Activity:</strong> Highest rate recorded during <strong>{peak_hour} UTC</strong> at <strong>{peak_count} QSOs/hr</strong>.</li>
        <li><strong>Primary Band:</strong> <strong>{top_band}</strong> was the most active band with <strong>{data['band_totals'][top_band]} contacts</strong> ({(data['band_totals'][top_band]/data['total_qsos'])*100:.1f}% of total).</li>
        <li><strong>Primary Mode:</strong> <strong>{top_mode}</strong> accounted for <strong>{data['mode_totals'][top_mode]} contacts</strong>.</li>
        <li><strong>Multipliers:</strong> Secured <strong>{data['multipliers']} unique multipliers</strong> across WA counties, US states, and Canadian provinces.</li>
    </ul>
    """

def generate_mode_histogram(time_bins):
    sorted_times = sorted(time_bins.keys())
    cw_counts = [time_bins[t]["CW"] for t in sorted_times]
    ph_counts = [time_bins[t]["PH"] for t in sorted_times]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=sorted_times, y=cw_counts, name='CW', marker_color='#2b5c8f'))
    fig.add_trace(go.Bar(x=sorted_times, y=ph_counts, name='Phone', marker_color='#d9534f'))

    fig.update_layout(
        title='Operating Rate Over Time (Breakdown by Mode)',
        xaxis_title='UTC Hour', yaxis_title='Number of Contacts',
        barmode='stack', template='plotly_white',
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id="time_mode_chart")

def generate_band_histogram(time_bins_band, active_bands):
    sorted_times = sorted(time_bins_band.keys())
    band_colors = {
        "160m": "#7cfc00", "80m": "#e550e5", "40m": "#5959ff", 
        "20m": "#f2c40c", "15m": "#cca166", "10m": "#ff69b4", "6m": "#FF0000"
    }

    fig = go.Figure()
    for b in active_bands:
        counts = [time_bins_band[t][b] for t in sorted_times]
        fig.add_trace(go.Bar(
            x=sorted_times, y=counts, name=b, 
            marker_color=band_colors.get(b, '#7f7f7f')
        ))

    fig.update_layout(
        title='Operating Rate Over Time (Breakdown by Band)',
        xaxis_title='UTC Hour', yaxis_title='Number of Contacts',
        barmode='stack', template='plotly_white',
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id="time_band_chart")

def generate_wa_heatmap(county_counts):
    fips_list = []
    names = []
    values = []

    for code, (full_name, fips) in WA_COUNTIES_FIPS.items():
        total = sum(county_counts[code][b][m] for b in county_counts[code] for m in county_counts[code][b])
        fips_list.append(fips)
        names.append(full_name)
        values.append(total)

    fig = go.Figure(go.Choropleth(
        geojson=COUNTIES_GEOJSON, locations=fips_list, z=values, text=names,
        colorscale="Reds", autocolorscale=False, marker_line_color='white',
        marker_line_width=0.5, colorbar_title="QSOs"
    ))

    fig.update_layout(
        title_text="Contacts by Washington County",
        geo=dict(scope='usa', fitbounds="locations", visible=False),
        template='plotly_white', margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id="wa_map")

def generate_na_heatmap(state_counts):
    states = list(US_STATES.keys())
    values = [sum(state_counts[st][b][m] for b in state_counts[st] for m in state_counts[st][b]) for st in states]

    fig = go.Figure(go.Choropleth(
        locations=states, z=values, locationmode='USA-states',
        colorscale='Reds', marker_line_color='white', colorbar_title="QSOs"
    ))

    fig.update_layout(
        title_text='Contacts by US State',
        geo=dict(scope='usa', projection=dict(type='albers usa'), showlakes=True, lakecolor='rgb(255, 255, 255)'),
        template='plotly_white', margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id="usa_map")

def generate_ca_heatmap(prov_counts):
    prov_names = []
    values = []

    for code, full_name in CANADIAN_PROVINCES.items():
        total = sum(prov_counts[code][b][m] for b in prov_counts[code] for m in prov_counts[code][b])
        prov_names.append(full_name)
        values.append(total)

    fig = go.Figure(go.Choropleth(
        geojson=CANADA_GEOJSON,
        featureidkey="properties.name",
        locations=prov_names,
        z=values,
        colorscale='Reds',
        marker_line_color='white',
        colorbar_title="QSOs"
    ))

    fig.update_layout(
        title_text='Contacts by Canadian Province / Territory',
        geo=dict(
            scope='north america',
            center=dict(lat=56.1304, lon=-106.3468),
            projection_scale=2.2,
            showlakes=True,
            lakecolor='rgb(255, 255, 255)'
        ),
        template='plotly_white', margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id="canada_map")

def render_table_html(counts_dict, loc_reference, bands):
    html = """<table class="data-table">
        <thead>
            <tr>
                <th rowspan="2">Location</th>
                <th rowspan="2">Name</th>"""
    for b in bands:
        html += f'<th colspan="2">{b}</th>'
    html += '<th colspan="3">Total</th></tr><tr>'
    for _ in bands:
        html += '<th>CW</th><th>PH</th>'
    html += '<th>CW</th><th>PH</th><th>All</th></tr></thead><tbody>'

    for code in sorted(loc_reference.keys()):
        name = loc_reference[code]
        row_cw = 0
        row_ph = 0
        band_cells = ""
        
        for b in bands:
            cw = counts_dict[code][b]['CW']
            ph = counts_dict[code][b]['PH']
            row_cw += cw
            row_ph += ph
            band_cells += f"<td>{cw if cw else '-'}</td><td>{ph if ph else '-'}</td>"

        row_total = row_cw + row_ph
        active_class = 'class="active-row"' if row_total > 0 else ''
        
        html += f'<tr {active_class}><td><strong>{code}</strong></td><td>{name}</td>'
        html += band_cells
        html += f'<td><strong>{row_cw}</strong></td><td><strong>{row_ph}</strong></td><td><strong>{row_total}</strong></td></tr>'

    html += '</tbody></table>'
    return html

def render_dx_table_html(dx_counts, bands):
    if not dx_counts:
        return "<p style='text-align: center; color: #777;'>No DX contacts logged.</p>"
        
    html = """<table class="data-table">
        <thead>
            <tr>
                <th rowspan="2">Call / Loc</th>"""
    for b in bands:
        html += f'<th colspan="2">{b}</th>'
    html += '<th colspan="3">Total</th></tr><tr>'
    for _ in bands:
        html += '<th>CW</th><th>PH</th>'
    html += '<th>CW</th><th>PH</th><th>All</th></tr></thead><tbody>'

    for code in sorted(dx_counts.keys()):
        row_cw = 0
        row_ph = 0
        band_cells = ""
        
        for b in bands:
            cw = dx_counts[code][b]['CW']
            ph = dx_counts[code][b]['PH']
            row_cw += cw
            row_ph += ph
            band_cells += f"<td>{cw if cw else '-'}</td><td>{ph if ph else '-'}</td>"

        row_total = row_cw + row_ph
        
        html += f'<tr class="active-row"><td><strong>{code}</strong></td>'
        html += band_cells
        html += f'<td><strong>{row_cw}</strong></td><td><strong>{row_ph}</strong></td><td><strong>{row_total}</strong></td></tr>'

    html += '</tbody></table>'
    return html

def build_report(header_info, data, mode_chart, band_chart, wa_chart, na_chart, ca_chart):
    wa_table_html = render_table_html(data['county_counts'], WA_COUNTIES, data['active_bands'])
    state_table_html = render_table_html(data['state_counts'], US_STATES, data['active_bands'])
    prov_table_html = render_table_html(data['prov_counts'], CANADIAN_PROVINCES, data['active_bands'])
    dx_table_html = render_dx_table_html(data['dx_counts'], data['active_bands'])
    
    summary_html = generate_summary_text(data)
    callsign = header_info.get("CALLSIGN", "???")
    operating_locs = header_info.get("OPERATING_LOCATIONS", "N/A")

    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{callsign} - Salmon Run 2026 Contest Results</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0; padding: 0;
            background-color: #f8f9fa;
            color: #333;
        }}
        header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 2rem 1rem;
            text-align: center;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }}
        .card h3 {{
            margin: 0; font-size: 0.9rem; color: #666; text-transform: uppercase;
        }}
        .card .value {{
            font-size: 2rem; font-weight: bold; margin-top: 10px; color: #1e3c72;
        }}
        .section-block {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 30px;
        }}
        h2 {{ border-bottom: 2px solid #eef2f5; padding-bottom: 10px; color: #2c3e50; }}
        .table-wrapper {{
            max-height: 450px;
            overflow-y: auto;
            border: 1px solid #dee2e6;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}
        .data-table th, .data-table td {{
            padding: 8px 10px;
            text-align: center;
            border: 1px solid #dee2e6;
        }}
        .data-table thead {{
            position: sticky; top: 0; background-color: #f1f3f5; z-index: 2;
        }}
        .data-table tr.active-row {{ background-color: #e7f5ff; }}
        .data-table tr:hover {{ background-color: #f8f9fa; }}
        .summary-box {{
            line-height: 1.6;
            font-size: 1rem;
            color: #444;
        }}
        .summary-box ul {{
            margin-top: 10px;
            padding-left: 20px;
        }}
        .summary-box li {{
            margin-bottom: 6px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Salmon Run 2026 Contest Report</h1>
        <p>Station: <strong>{callsign}</strong> | Operating Location(s): <strong>{operating_locs}</strong></p>
    </header>

    <div class="container">
        <!-- Executive Summary Block -->
        <div class="section-block">
            <h2>Contest Progress & Performance Summary</h2>
            <div class="summary-box">
                {summary_html}
            </div>
        </div>

        <!-- Summary Cards -->
        <div class="cards-grid">
            <div class="card"><h3>Total QSOs</h3><div class="value">{data['total_qsos']}</div></div>
            <div class="card"><h3>QSO Points</h3><div class="value">{data['qso_points']}</div></div>
            <div class="card"><h3>Multipliers</h3><div class="value">{data['multipliers']}</div></div>
            <div class="card"><h3>Bonus Points</h3><div class="value">{data['bonus_points']}</div></div>
            <div class="card"><h3>Final Score</h3><div class="value">{data['final_score']:,}</div></div>
        </div>

        <!-- Operating Rate Charts -->
        <div class="section-block">
            <h2>Operating Rate Charts</h2>
            {mode_chart}
            <div style="margin-top: 30px;">
                {band_chart}
            </div>
        </div>

        <!-- Heatmaps Section -->
        <div class="section-block">
            <h2>Geographic Heatmaps</h2>
            {wa_chart}
            <div style="margin-top: 30px;">
                {na_chart}
            </div>
            <div style="margin-top: 30px;">
                {ca_chart}
            </div>
        </div>

        <!-- Data Tables -->
        <div class="section-block">
            <h2>Washington Counties Breakdown</h2>
            <div class="table-wrapper">
                {wa_table_html}
            </div>
        </div>

        <div class="section-block">
            <h2>US States Breakdown</h2>
            <div class="table-wrapper">
                {state_table_html}
            </div>
        </div>

        <div class="section-block">
            <h2>Canadian Provinces Breakdown</h2>
            <div class="table-wrapper">
                {prov_table_html}
            </div>
        </div>

        <div class="section-block">
            <h2>DX & Other Contacts Breakdown</h2>
            <div class="table-wrapper">
                {dx_table_html}
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html_document

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_report_3.py <path_to_cabrillo_file.log>")
        sys.exit(1)

    cabrillo_file = sys.argv[1]
    header_info, qsos = parse_cabrillo(cabrillo_file)
    data = process_log_data(qsos)

    mode_chart = generate_mode_histogram(data['time_bins_mode'])
    band_chart = generate_band_histogram(data['time_bins_band'], data['active_bands'])
    wa_chart = generate_wa_heatmap(data['county_counts'])
    na_chart = generate_na_heatmap(data['state_counts'])
    ca_chart = generate_ca_heatmap(data['prov_counts'])

    html_report = build_report(header_info, data, mode_chart, band_chart, wa_chart, na_chart, ca_chart)
    
    output_filename = "salmon_run_2026_report.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_report)

    print(f"Report generated successfully: {output_filename}")

if __name__ == "__main__":
    main()
