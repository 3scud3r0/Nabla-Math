async function loadSnapshot() {
  const label = document.getElementById('snapshot-date');
  try {
    const response = await fetch('data/status.json', {cache: 'no-store'});
    if (!response.ok) throw new Error('snapshot indisponível');
    const snapshot = await response.json();
    for (const [id, value] of Object.entries({
      'metric-records': snapshot.public_curated_records,
      'metric-participants': snapshot.verified_public_participants,
      'metric-phases': snapshot.completed_phases
    })) {
      if (!Number.isSafeInteger(value) || value < 0) throw new Error('métrica inválida');
      document.getElementById(id).textContent = String(value);
    }
    label.textContent = 'Snapshot: ' + snapshot.as_of + ' · Atualização por publicação versionada, sem telemetria em tempo real.';
  } catch (error) {
    label.textContent = 'Snapshot indisponível; consulte o repositório para confirmar o estado.';
  }
}
loadSnapshot();
