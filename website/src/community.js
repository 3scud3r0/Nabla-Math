export function anonymizedMetrics(snapshot) {
  return { participants: Number(snapshot?.participants || 0), tasks: Number(snapshot?.tasks || 0), source: "snapshot" };
}
