import { auditRows, parseCSV, summarize, toCSV, toGeoJSON, DISTRICT_EXTENT } from './workbench.mjs';

const $ = id => document.getElementById(id);
let records = [];
let map;
let markerLayer;
let activeMapFilter = 'all';

function toast(message) {
  const el = $('toast'); el.textContent = message; el.classList.add('show');
  clearTimeout(toast.timer); toast.timer = setTimeout(() => el.classList.remove('show'), 2800);
}

function getProfile() {
  return {
    dataset_name: $('meta-name').value.trim() || 'District 8 Maintenance Activity Demo',
    data_steward: $('meta-owner').value.trim() || 'Unassigned',
    source_system: $('meta-source').value.trim() || 'Unspecified',
    update_cadence: $('meta-cadence').value,
    coordinate_reference_system: $('meta-crs').value,
    purpose: $('meta-purpose').value.trim(),
    classification: 'Synthetic demonstration data',
    data_owner_contact: 'Not provided in demo',
    review_extent: 'Illustrative District 8 envelope; not an authoritative boundary',
    loaded_at: new Date().toISOString(),
  };
}

function download(name, body, type) {
  const blob = new Blob([body], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = name;
  document.body.append(anchor); anchor.click(); anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 800);
}

function validCoordinate(row) {
  if (!String(row.latitude ?? '').trim() || !String(row.longitude ?? '').trim()) return false;
  const lat = Number(row.latitude), lon = Number(row.longitude);
  return Number.isFinite(lat) && Number.isFinite(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
}

function stateColor(state) { return state === 'ready' ? '#378665' : state === 'review' ? '#d19230' : '#c45a46'; }
function stateText(state) { return state === 'ready' ? 'Ready to publish' : state === 'review' ? 'Needs review' : 'Invalid'; }
function markerIcon(row) {
  const color = stateColor(row._state);
  const label = row._state === 'ready' ? '✓' : row._state === 'review' ? '!' : '×';
  return L.divIcon({ className: '', html: `<div class="record-pin ${row._state}" style="background:${color}">${label}</div>`, iconSize: [18, 18], iconAnchor: [9, 9] });
}

function initMap() {
  const host = $('map');
  if (!window.L) { host.innerHTML = '<div class="rule-none">Map library could not load. Connect to the internet and refresh.</div>'; return; }
  map = L.map(host, { zoomControl: false, preferCanvas: true }).setView([34.22, -117.16], 8);
  L.control.zoom({ position: 'bottomright' }).addTo(map);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: '© OpenStreetMap contributors © CARTO', subdomains: 'abcd', maxZoom: 19 }).addTo(map);
  L.rectangle([[DISTRICT_EXTENT.south, DISTRICT_EXTENT.west], [DISTRICT_EXTENT.north, DISTRICT_EXTENT.east]], { color: '#55836a', weight: 1, opacity: .75, dashArray: '5 5', fillColor: '#76ab7e', fillOpacity: .035, interactive: false }).addTo(map);
  markerLayer = L.layerGroup().addTo(map);
  map.fitBounds([[DISTRICT_EXTENT.south, DISTRICT_EXTENT.west], [DISTRICT_EXTENT.north, DISTRICT_EXTENT.east]], { padding: [15, 15] });
}

function renderMap() {
  if (!markerLayer) return;
  markerLayer.clearLayers();
  const mappable = records.filter(validCoordinate);
  mappable.filter(row => activeMapFilter === 'all' || (activeMapFilter === 'ready' && row._state === 'ready') || (activeMapFilter === 'flagged' && row._state !== 'ready')).forEach(row => {
    const marker = L.marker([Number(row.latitude), Number(row.longitude)], { icon: markerIcon(row), title: row.work_order_id || `CSV row ${row._row}` });
    const issues = row._issues.length ? row._issues.map(issue => `<br>• ${escapeHtml(issue.message)}`).join('') : '<br>No validation issues.';
    marker.bindPopup(`<div class="popup-name">${escapeHtml(row.work_order_id || `Row ${row._row}`)} · ${stateText(row._state)}</div><div class="popup-sub">${escapeHtml(row.activity_type || 'Unknown activity')} · ${escapeHtml(row.route || 'No route')}<br>${escapeHtml(row.location_description || 'No location description')}${issues}</div>`);
    marker.record = row;
    marker.addTo(markerLayer);
  });
  $('mapped-count').textContent = mappable.length;
}

function renderRules(summary) {
  $('rule-list').innerHTML = summary.rules.length ? summary.rules.slice(0, 9).map(rule => `
    <div class="rule-row"><span class="rule-symbol ${rule.severity}">${rule.severity === 'error' ? '!' : '◷'}</span><span class="rule-name">${escapeHtml(rule.label)}</span><span class="rule-count">${rule.count}</span></div>`).join('') : '<div class="rule-none">No issues found. All rows pass the current profile checks.</div>';
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}

function renderTable() {
  const filter = $('record-filter').value;
  const query = $('search-records').value.trim().toLowerCase();
  const filtered = records.filter(row => (filter === 'all' || row._state === filter) && (!query || `${row.work_order_id} ${row.activity_type} ${row.route} ${row.location_description}`.toLowerCase().includes(query)));
  const visible = filtered.slice(0, 100);
  $('record-rows').innerHTML = visible.map(row => {
    const coords = validCoordinate(row) ? `${Number(row.latitude).toFixed(4)}, ${Number(row.longitude).toFixed(4)}` : '—';
    return `<tr data-row="${row._row}" tabindex="0" aria-label="${escapeHtml(row.work_order_id || `CSV row ${row._row}`)} ${stateText(row._state)}"><td><span class="work-id"><i class="row-indicator ${row._state}"></i>${escapeHtml(row.work_order_id || `Row ${row._row}`)}</span></td><td>${escapeHtml(row.activity_type || '—')}</td><td><span class="route-main">${escapeHtml(row.route || 'No route')}</span><span class="route-sub">${escapeHtml(row.location_description || 'Location not supplied')}</span></td><td class="coords">${coords}</td><td><span class="quality-pill ${row._state}">${stateText(row._state)}</span></td><td class="row-open">›</td></tr>`;
  }).join('');
  $('table-count').textContent = `Showing ${visible.length} of ${filtered.length} matching records${filtered.length > visible.length ? ' · refine search to see more' : ''}`;
  document.querySelectorAll('#record-rows tr').forEach(tr => {
    const open = () => {
      const row = records.find(record => record._row === Number(tr.dataset.row));
      if (!row) return;
      if (map && validCoordinate(row)) { map.flyTo([Number(row.latitude), Number(row.longitude)], 11, { duration: .65 }); markerLayer.eachLayer(marker => { if (marker.record?._row === row._row) marker.openPopup(); }); }
      if (row._issues.length) toast(`${row.work_order_id}: ${row._issues.length} validation issue${row._issues.length === 1 ? '' : 's'}`);
      else toast(`${row.work_order_id} passes all current checks.`);
    };
    tr.addEventListener('click', open);
    tr.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); open(); } });
  });
}

function render() {
  const summary = summarize(records);
  $('score').textContent = summary.score; $('score-bar').style.width = `${summary.score}%`;
  $('score-label').textContent = summary.score >= 85 ? 'Strong readiness' : summary.score >= 60 ? 'Review recommended' : 'Action needed';
  $('total-count').textContent = summary.total; $('ready-count').textContent = summary.ready;
  $('review-count').textContent = summary.review; $('invalid-count').textContent = summary.invalid;
  $('issue-count').textContent = summary.issues; $('duplicate-count').textContent = summary.duplicates; $('checked-count').textContent = summary.total;
  $('side-record-count').textContent = `${summary.total} records · demo profile`;
  $('side-dataset').textContent = $('meta-name').value.replace(' — Demo', '') || 'Maintenance activities';
  $('updated-at').textContent = `Updated ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  renderRules(summary); renderTable(); renderMap();
}

function loadRows(rows, label = 'Dataset loaded in browser. No records were uploaded.') {
  records = auditRows(rows); selectedId = null; render(); $('upload-status').textContent = `${records.length} rows loaded`;
  toast(label);
}

async function loadSample() {
  const response = await fetch(new URL('../data/district8_maintenance_demo.csv', import.meta.url));
  if (!response.ok) throw new Error('Could not load the bundled sample CSV. Run the app from a local web server.');
  loadRows(parseCSV(await response.text()), 'Synthetic sample data loaded.');
}

$('record-filter').addEventListener('change', renderTable);
$('search-records').addEventListener('input', renderTable);
document.querySelectorAll('[data-map-filter]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-map-filter]').forEach(item => item.classList.toggle('active', item === button));
  activeMapFilter = button.dataset.mapFilter; renderMap();
}));
$('zoom-map').addEventListener('click', () => map?.fitBounds([[DISTRICT_EXTENT.south, DISTRICT_EXTENT.west], [DISTRICT_EXTENT.north, DISTRICT_EXTENT.east]], { padding: [15, 15] }));
$('refresh-demo').addEventListener('click', () => loadSample().catch(error => toast(error.message)));
$('load-sample').addEventListener('click', () => loadSample().catch(error => toast(error.message)));
$('csv-file').addEventListener('change', async event => {
  const file = event.target.files?.[0]; if (!file) return;
  try { loadRows(parseCSV(await file.text()), `${file.name} processed locally in your browser.`); }
  catch (error) { $('upload-status').textContent = error.message; toast(`CSV not loaded: ${error.message}`); }
  event.target.value = '';
});
$('save-profile').addEventListener('click', () => toast('Dataset profile saved for this browser session.'));
$('export-geojson').addEventListener('click', () => {
  const output = toGeoJSON(records, { datasetName: $('meta-name').value, steward: $('meta-owner').value });
  download('district8-maintenance-ready.geojson', JSON.stringify(output, null, 2), 'application/geo+json');
  toast(`${output.features.length} clean records exported. Review and warning rows were excluded.`);
});
$('download-report').addEventListener('click', () => {
  const output = { report_title: 'Maintenance GIS data quality report', generated_at: new Date().toISOString(), dataset_profile: getProfile(), summary: summarize(records), records: records.map(row => ({ work_order_id: row.work_order_id || null, source_row: row._row, quality_state: row._state, issues: row._issues })) };
  download('district8-data-quality-report.json', JSON.stringify(output, null, 2), 'application/json');
  toast('QA report downloaded.');
});
$('download-metadata').addEventListener('click', () => download('district8-dataset-metadata.json', JSON.stringify(getProfile(), null, 2), 'application/json'));

initMap();
loadSample().catch(error => { $('upload-status').textContent = error.message; toast(error.message); });
