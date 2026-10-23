# Data dictionary

The bundled CSV is entirely synthetic and follows an illustrative IMMS-style structure. It is not copied from an agency, vendor, contractor, or employee record.

## Input columns

| Column | Type | Required | Description |
|---|---|---:|---|
| `work_order_id` | String | Yes | Fictional work-order identifier. Used for duplicate screening. |
| `activity_type` | Coded string | Yes | One of the configured sample maintenance categories. |
| `work_status` | Coded string | Yes | `Planned`, `In Progress`, `Complete`, or `On Hold`. |
| `district` | Integer-like string | No | Synthetic district label, included as context. |
| `route` | String | Yes | Sample route label such as `I-10` or `SR-210`. |
| `location_description` | String | No | Fictional general location label. |
| `latitude` | Decimal | Yes | WGS 84 latitude in decimal degrees. |
| `longitude` | Decimal | Yes | WGS 84 longitude in decimal degrees. |
| `acres` | Decimal | No | Synthetic area estimate associated with the work order. |
| `scheduled_date` | Date | Yes | Demo schedule date in `YYYY-MM-DD` format. |
| `updated_at` | Datetime | No | Synthetic source update timestamp. |
| `source_system` | String | No | Synthetic source label. |

Additional CSV columns are retained in exports. The application does not use personal information.

## GeoJSON properties

The GeoJSON export retains all original non-internal CSV fields. It includes only ready rows and adds top-level metadata for classification, steward, output CRS, generation time, and the export rule. Coordinates use `[longitude, latitude]` order.
