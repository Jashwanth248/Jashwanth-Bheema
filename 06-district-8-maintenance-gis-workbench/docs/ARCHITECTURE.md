# Architecture

## Application flow

1. The browser loads a CSV from the bundled sample file or a file selected locally by the user.
2. `src/workbench.mjs` parses the CSV and normalizes cell values.
3. The validation engine applies schema, domain, date, duplicate, coordinate, and demo extent checks.
4. The interface renders aggregate quality results, row-level findings, and mappable locations.
5. A data steward reviews and corrects source data. The prototype does not silently alter input records.
6. The user may export the clean subset as GeoJSON, all rows with review annotations as CSV, a QA report, or a metadata profile.

## Components

- `src/workbench.mjs` is a dependency-free module for CSV parsing, validation, summaries, and output serialization. It is covered by Node's built-in test runner.
- `src/app.mjs` connects the workbench module to the browser interface and Leaflet map.
- `index.html` contains the interface structure and loads Leaflet and the CARTO basemap for the map preview.
- `data/district8_maintenance_demo.csv` contains synthetic records deliberately seeded with several types of quality issues.
- `docs/QUALITY_RULES.md` and `docs/DATA_DICTIONARY.md` define the assumptions used by the demo.

## Coordinate handling

The input profile expects decimal-degree latitude and longitude in the WGS 84 reference system. The map uses Leaflet's web map projection internally. GeoJSON output follows OGC CRS84 coordinate order: `[longitude, latitude]`. A broad rectangular extent is used as a review warning only; it is not a district boundary and cannot replace authoritative district geometry.

## Production design considerations

A real maintenance system would require approved source interfaces, access controls, audit and retention policies, versioned schemas, geometry-specific validation against authoritative reference data, metadata ownership, service availability monitoring, and a publication workflow approved by GIS data stewards. A production web map could consume secured ArcGIS Enterprise or ArcGIS Online feature services; this portfolio app only exports files and does not publish services.

Any official readiness thresholds, accepted code lists, CRS requirements, lineage rules, or quality standards must come from the data owner. This demo uses illustrative rules only and does not infer official requirements.
