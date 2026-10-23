# Demonstration quality rules

These checks are example rules for a portfolio demo. They are not official Caltrans validation requirements. Confirm schema, domains, coordinate systems, and spatial boundaries with the dataset owner before applying a production profile.

| Rule | Level | Condition | Output behavior |
|---|---|---|---|
| Required fields | Error | A required ID, activity, status, route, coordinate, or scheduled date is blank. | Row is invalid and excluded from clean GeoJSON. |
| Unique work-order ID | Error | A work-order identifier appears more than once, case-insensitively. | All duplicate rows are flagged. |
| Activity domain | Error | Activity is outside the configured demo list. | Row is invalid. |
| Status domain | Error | Status is outside the configured demo list. | Row is invalid. |
| Route format | Warning | Route does not match the demo `I-###` or `SR-###` pattern. | Row needs review. |
| Coordinate validity | Error | Latitude or longitude is non-numeric or outside global coordinate ranges. | Row is invalid and cannot be mapped. |
| Coordinate order | Error | Coordinate values appear to be reversed based on the demo review envelope. | Row is invalid pending correction. |
| Review extent | Warning | A valid point is outside the broad illustrative District 8 extent. | Row needs location verification. |
| Duplicate location | Warning | Multiple rows share coordinates rounded to five decimal places. | Row needs duplicate/generalization review. |
| ISO date | Error | Scheduled date is not a valid `YYYY-MM-DD` calendar date. | Row is invalid. |
| Non-negative acreage | Error | Supplied acreage is not numeric or is below zero. | Row is invalid. |

## Readiness score

The displayed score is a simple portfolio demonstration formula: ready rows contribute 1 point, rows with warnings only contribute 0.6 points, invalid rows contribute 0, and the result is converted to a percentage. It is not statistically calibrated and should not be used as an official data quality score.

## Export gate

Only rows classified as ready are included in the GeoJSON export. The QA CSV includes all rows plus a state and issue-code list. The QA report records the findings and metadata entered for the session. Re-running the checks does not modify source values.
