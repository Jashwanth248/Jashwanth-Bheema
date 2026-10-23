# District 8 Maintenance GIS Data Workbench

A browser-based GIS data stewardship workbench that turns a maintenance activity CSV into a reviewed spatial dataset. It demonstrates a practical workflow for bringing tabular field activity records into GIS, checking data quality, documenting dataset metadata, and preparing clean features for spatial analysis.

> **Portfolio demonstration only.** The bundled records, IDs, locations, route references, and metadata are synthetic. This project is not connected to Caltrans, IMMS, ArcGIS Enterprise, or any agency system. Its district envelope is illustrative, its rules are demo rules, and its readiness score is not an official measure.

## What it does

- Loads a bundled synthetic IMMS-style CSV or another local CSV selected by the user.
- Parses quoted CSV fields and keeps the uploaded file in the browser; records are not sent to an API.
- Checks required attributes, duplicate work-order IDs, activity and status values, route format, coordinate validity and order, review extent, duplicate coordinates, dates, and acreage values.
- Separates rows into **Ready to publish**, **Needs review**, and **Invalid** states.
- Maps records with usable coordinates and lets the user filter the map by quality state.
- Shows rule counts, record-level issues, and a data readiness score derived from the demo rules.
- Exports passing records as WGS 84 GeoJSON, exports all records with quality annotations as CSV, and downloads a JSON QA report and metadata profile.
- Includes a sample data dictionary, schema notes, quality rules, architecture notes, and automated tests.

## Quick start

Requirements: Python 3 for a simple local web server; Node.js 20+ only for running the automated tests. No package installation or API keys are required. An internet connection is needed for the Leaflet library, fonts, and basemap tiles.

```bash
git clone https://github.com/Jashwanth248/Jashwanth-Bheema.git
cd Jashwanth-Bheema/06-district-8-maintenance-gis-workbench
python3 -m http.server 8000
```

Open <http://localhost:8000> in a browser. Use **Choose CSV** to load your own local file, or choose **Reload sample dataset** to restore the included demonstration records.

Run the tests from this project folder:

```bash
node --test
```

## CSV input fields

The core checks expect these columns:

| Field | Required | Example |
|---|---:|---|
| `work_order_id` | Yes | `MNT-24001` |
| `activity_type` | Yes | `Brush clearing` |
| `work_status` | Yes | `Planned` |
| `route` | Yes | `I-10` or `SR-210` |
| `latitude` | Yes | `34.055` |
| `longitude` | Yes | `-117.205` |
| `scheduled_date` | Yes | `2026-10-24` |
| `acres` | No | `12.5` |
| `location_description` | No | `West of Redlands` |

Additional columns are retained in the CSV review export and GeoJSON properties. See [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).

## Quality workflow

The bundled profile uses explicit required fields, activity/status domains, ISO date checks, non-negative acreage checks, a route naming pattern, coordinate range and order checks, duplicate ID and location screening, and a broad illustrative District 8 envelope. The screen is designed to make data problems visible before GIS publication. Review rules and their limitations are in [`docs/QUALITY_RULES.md`](docs/QUALITY_RULES.md).

The GeoJSON export is intentionally strict: it includes only rows with no errors **and** no warnings. The QA CSV keeps every row and adds `quality_state` and `quality_issues` so a data steward can review and correct flagged records. The JSON report captures the run summary, row-level findings, and editable metadata profile.

## Technology

| Component | Technology |
|---|---|
| Interface | HTML and CSS |
| CSV, validation, score, and export logic | Dependency-free JavaScript ES modules |
| Spatial preview | Leaflet 1.9 and CARTO light basemap |
| GIS interchange | GeoJSON / OGC CRS84 (WGS 84 longitude, latitude) |
| Automated checks | Node.js built-in test runner |
| Local hosting | Python built-in HTTP server |

## Project structure

```text
.
├── data/district8_maintenance_demo.csv
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   └── QUALITY_RULES.md
├── src/
│   ├── app.mjs
│   ├── styles.css
│   └── workbench.mjs
├── tests/workbench.test.mjs
└── index.html
```

## Alignment to the GIS Coordinator role

This project demonstrates a small, reviewable version of the work described in the position duties: integrating non-spatial maintenance records into GIS, designing and applying data-quality rules, defining metadata and stewardship details, mapping and summarizing data, and preparing shareable spatial outputs. It also shows a simple web GIS interface and a reproducible validation workflow.

It does not demonstrate access to the agency's systems, authoritative boundary data, official standards, or production GIS services. The documented production adaptation path explains what would need to be governed and validated before using approved operational data.

## License

MIT. See [`LICENSE`](LICENSE).
