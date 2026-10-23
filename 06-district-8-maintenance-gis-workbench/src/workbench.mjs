export const DISTRICT_EXTENT = { south: 33.55, north: 35.12, west: -118.12, east: -115.62 };
export const ACTIVITY_TYPES = ['Brush clearing', 'Fuel reduction', 'Tree trimming', 'Fire break', 'Debris removal', 'Drainage inspection'];
export const WORK_STATUSES = ['Planned', 'In Progress', 'Complete', 'On Hold'];
export const REQUIRED_FIELDS = ['work_order_id', 'activity_type', 'work_status', 'route', 'latitude', 'longitude', 'scheduled_date'];

const trimRow = row => Object.fromEntries(Object.entries(row).map(([key, value]) => [key.trim(), String(value ?? '').trim()]));

export function parseCSV(source) {
  const rows = [];
  let row = [], cell = '', quoted = false;
  for (let i = 0; i < source.length; i++) {
    const char = source[i];
    if (quoted) {
      if (char === '"' && source[i + 1] === '"') { cell += '"'; i++; }
      else if (char === '"') quoted = false;
      else cell += char;
    } else if (char === '"' && cell.length === 0) quoted = true;
    else if (char === ',') { row.push(cell); cell = ''; }
    else if (char === '\n' || char === '\r') {
      if (char === '\r' && source[i + 1] === '\n') i++;
      row.push(cell); cell = '';
      if (row.some(value => value.trim() !== '')) rows.push(row);
      row = [];
    } else cell += char;
  }
  row.push(cell);
  if (row.some(value => value.trim() !== '')) rows.push(row);
  if (quoted) throw new Error('The CSV contains a quoted field that was not closed.');
  if (rows.length < 2) throw new Error('The CSV needs a header row and at least one data row.');
  const headers = rows[0].map(value => value.trim().replace(/^\uFEFF/, ''));
  if (new Set(headers).size !== headers.length) throw new Error('The CSV has duplicate column names.');
  return rows.slice(1).map(values => trimRow(Object.fromEntries(headers.map((header, index) => [header, values[index] ?? '']))));
}

const validISODate = value => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(`${value}T00:00:00Z`);
  return !Number.isNaN(date.valueOf()) && date.toISOString().slice(0, 10) === value;
};

export function auditRows(inputRows) {
  const rows = inputRows.map((source, index) => ({ ...trimRow(source), _row: index + 2, _issues: [], _state: 'ready' }));
  const idCounts = new Map();
  rows.forEach(row => { const key = (row.work_order_id || '').toUpperCase(); if (key) idCounts.set(key, (idCounts.get(key) || 0) + 1); });
  const coordinateCounts = new Map();
  rows.forEach(row => {
    const latitude = Number(row.latitude), longitude = Number(row.longitude);
    if (Number.isFinite(latitude) && Number.isFinite(longitude)) {
      const key = `${latitude.toFixed(5)},${longitude.toFixed(5)}`;
      coordinateCounts.set(key, (coordinateCounts.get(key) || 0) + 1);
    }
  });
  rows.forEach(row => {
    const add = (code, severity, message) => row._issues.push({ code, severity, message });
    REQUIRED_FIELDS.forEach(field => { if (!row[field]) add('required_field', 'error', `Required field ${field} is empty.`); });
    if (row.work_order_id && idCounts.get(row.work_order_id.toUpperCase()) > 1) add('duplicate_id', 'error', `Work order ID ${row.work_order_id} appears more than once.`);
    if (row.activity_type && !ACTIVITY_TYPES.includes(row.activity_type)) add('activity_domain', 'error', `Activity type “${row.activity_type}” is not in the approved demo list.`);
    if (row.work_status && !WORK_STATUSES.includes(row.work_status)) add('status_domain', 'error', `Status “${row.work_status}” is not in the approved demo list.`);
    if (row.route && !/^(I-\d{1,3}|SR-\d{1,3})$/.test(row.route.toUpperCase())) add('route_format', 'warning', 'Route should use an I-### or SR-### format.');
    const latitude = Number(row.latitude), longitude = Number(row.longitude);
    if (row.latitude && row.longitude) {
      if (!Number.isFinite(latitude) || !Number.isFinite(longitude) || latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) {
        add('coordinate_range', 'error', 'Latitude or longitude is not a valid decimal-degree coordinate.');
      } else {
        if (latitude >= DISTRICT_EXTENT.west && latitude <= DISTRICT_EXTENT.east && longitude >= DISTRICT_EXTENT.south && longitude <= DISTRICT_EXTENT.north) add('coordinate_order', 'error', 'Coordinates may be reversed; the latitude value falls in the longitude range.');
        if (latitude < DISTRICT_EXTENT.south || latitude > DISTRICT_EXTENT.north || longitude < DISTRICT_EXTENT.west || longitude > DISTRICT_EXTENT.east) add('outside_extent', 'warning', 'Point falls outside the illustrative District 8 review extent. Verify its location.');
        const key = `${latitude.toFixed(5)},${longitude.toFixed(5)}`;
        if (coordinateCounts.get(key) > 1) add('duplicate_location', 'warning', 'Multiple rows share the same rounded coordinates. Check for duplicate or generalized locations.');
      }
    }
    if (row.scheduled_date && !validISODate(row.scheduled_date)) add('date_format', 'error', 'Scheduled date must be a real date in YYYY-MM-DD format.');
    if (row.acres !== undefined && row.acres !== '') {
      const acres = Number(row.acres);
      if (!Number.isFinite(acres) || acres < 0) add('acre_value', 'error', 'Acres must be a non-negative number.');
    }
    const hasError = row._issues.some(issue => issue.severity === 'error');
    const hasWarning = row._issues.some(issue => issue.severity === 'warning');
    row._state = hasError ? 'invalid' : hasWarning ? 'review' : 'ready';
  });
  return rows;
}

export function summarize(rows) {
  const counts = { total: rows.length, ready: 0, review: 0, invalid: 0, issues: 0, duplicates: 0 };
  const rules = new Map();
  rows.forEach(row => {
    counts[row._state]++;
    row._issues.forEach(issue => {
      counts.issues++;
      const entry = rules.get(issue.code) || { code: issue.code, label: issue.message.replace(/[“"].*?[”"]/, 'value'), count: 0, severity: issue.severity };
      entry.count++;
      rules.set(issue.code, entry);
      if (issue.code === 'duplicate_id') counts.duplicates++;
    });
  });
  const score = counts.total ? Math.max(0, Math.round(100 * (counts.ready + counts.review * 0.6) / counts.total)) : 0;
  return { ...counts, score, rules: [...rules.values()].sort((a, b) => b.count - a.count || a.code.localeCompare(b.code)) };
}

export function toGeoJSON(rows, { datasetName = 'District 8 Maintenance Activity Demo', steward = 'Maintenance Data Steward (sample)' } = {}) {
  const features = rows.filter(row => row._state === 'ready').map(row => ({
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [Number(row.longitude), Number(row.latitude)] },
    properties: Object.fromEntries(Object.entries(row).filter(([key]) => !key.startsWith('_'))),
  }));
  return {
    type: 'FeatureCollection',
    name: datasetName,
    metadata: { classification: 'Synthetic demonstration data', steward, coordinate_reference_system: 'OGC:CRS84 / WGS 84', generated_at: new Date().toISOString(), quality_rule: 'Only rows with no validation errors or warnings are included.' },
    features,
  };
}

export function toCSV(rows) {
  const fields = [...new Set([...rows.flatMap(row => Object.keys(row).filter(key => !key.startsWith('_'))), 'quality_state', 'quality_issues'])];
  const quote = value => `"${String(value ?? '').replaceAll('"', '""')}"`;
  return [fields.map(quote).join(','), ...rows.map(row => fields.map(field => quote(field === 'quality_state' ? row._state : field === 'quality_issues' ? row._issues.map(issue => `${issue.severity}:${issue.code}`).join('|') : row[field])).join(','))].join('\r\n');
}
