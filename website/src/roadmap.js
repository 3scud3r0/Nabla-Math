export async function loadRoadmap(url = "data/status.json") {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`status ${response.status}`);
  return response.json();
}
