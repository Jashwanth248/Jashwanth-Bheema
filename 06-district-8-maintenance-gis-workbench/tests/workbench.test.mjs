import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { auditRows, parseCSV, summarize, toCSV, toGeoJSON } from '../src/workbench.mjs';

const sample = await readFile(new URL('../data/district8_maintenance_demo.csv', import.meta.url), 'utf8');

test('CSV parser preserves quoted commas and escaped quotes', () => {
  const rows = parseCSV('id,note\n1,"Cajon Pass, north"\n2,"crew said ""check slope"""');
  assert.equal(rows[0].note, 'Cajon Pass, north');
  assert.equal(rows[1].note, 'crew said "check slope"');
});

test('sample data loads, runs quality rules, and exposes expected issue categories', () => {
  const rows = auditRows(parseCSV(sample));
  const result = summarize(rows);
  assert.equal(result.total, 23);
  assert.ok(result.ready > 0);
  assert.ok(result.review > 0);
  assert.ok(result.invalid > 0);
  assert.ok(result.rules.some(rule => rule.code === 'duplicate_location'));
  assert.ok(result.rules.some(rule => rule.code === 'outside_extent'));
  assert.ok(result.rules.some(rule => rule.code === 'acre_value'));
  assert.ok(result.rules.some(rule => rule.code === 'date_format'));
});

test('quality gates prevent warnings and errors from appearing in clean GIS export', () => {
  const rows = auditRows(parseCSV(sample));
  const output = toGeoJSON(rows, { datasetName: 'Test', steward: 'Steward' });
  assert.equal(output.metadata.classification, 'Synthetic demonstration data');
  assert.equal(output.metadata.steward, 'Steward');
  assert.equal(output.features.length, rows.filter(row => row._state === 'ready').length);
  for (const feature of output.features) {
    assert.equal(feature.geometry.type, 'Point');
    assert.equal(feature.geometry.coordinates.length, 2);
    assert.ok(feature.properties.work_order_id);
  }
});

test('CSV review export includes quality state and escaped fields', () => {
  const rows = auditRows(parseCSV('work_order_id,activity_type,work_status,route,latitude,longitude,scheduled_date,acres,location_description\nQ-1,Brush clearing,Planned,I-10,34.1,-117.2,2026-10-28,2,"River, east"'));
  const csv = toCSV(rows);
  assert.match(csv, /quality_state/);
  assert.match(csv, /"River, east"/);
  assert.match(csv, /"ready"/);
});

test('malformed quote and duplicate headers are rejected', () => {
  assert.throws(() => parseCSV('id,note\n1,"unfinished'), /not closed/);
  assert.throws(() => parseCSV('id,id\n1,2'), /duplicate column/);
});
