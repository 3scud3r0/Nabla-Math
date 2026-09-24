export function filterRecords(records, query) {
  const normalized = String(query || "").toLowerCase();
  return records.filter((record) => JSON.stringify(record).toLowerCase().includes(normalized));
}
