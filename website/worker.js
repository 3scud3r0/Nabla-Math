/* Somente trabalho demonstrativo e local. Não realiza rede nem executa código do usuário. */
let shouldStop = false;

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

async function sha256(value) {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, '0')).join('');
}

async function makeRecord(kind, n) {
  const x = BigInt(n);
  const base = kind === 'doubling'
    ? {schema_version: 1, domain: 'integer_arithmetic_demo', task: 'x_plus_x_equals_two_x', input: {x: String(n)}, equation: `${n}+${n}=${String(2n * x)}`, computed_exactly: String(x + x), verified_locally: x + x === 2n * x, formal_proof: false}
    : {schema_version: 1, domain: 'integer_arithmetic_demo', task: 'nonzero_ratio', input: {x: String(n)}, condition: 'x != 0', equation: `(${n}+${n})/${n}=2`, computed_exactly: String((x + x) / x), verified_locally: x !== 0n && (x + x) / x === 2n, formal_proof: false};
  return {...base, content_id: await sha256(canonicalJson(base))};
}

self.onmessage = async ({data}) => {
  if (data?.type === 'stop') {
    shouldStop = true;
    return;
  }
  if (data?.type !== 'start' || !Number.isSafeInteger(data.count) || data.count < 1 || data.count > 5000) {
    self.postMessage({type: 'error', message: 'Tamanho de trabalho inválido.'});
    return;
  }

  shouldStop = false;
  const count = data.count;
  let completed = 0;
  try {
    while (completed < count && !shouldStop) {
      const records = [];
      const end = Math.min(completed + 25, count);
      for (let index = completed + 1; index <= end; index += 1) {
        records.push(await makeRecord('doubling', index));
        records.push(await makeRecord('nonzero_ratio', index));
      }
      completed = end;
      self.postMessage({type: 'batch', completed, records});
      await new Promise(resolve => setTimeout(resolve, 0));
    }
    self.postMessage({type: shouldStop ? 'stopped' : 'done', completed});
  } catch (error) {
    self.postMessage({type: 'error', message: String(error?.message || error)});
  }
};
