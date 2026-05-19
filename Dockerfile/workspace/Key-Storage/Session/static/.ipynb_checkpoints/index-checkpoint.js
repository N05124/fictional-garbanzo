/**
 * Credential Transmission Dashboard
 * Interfaces with remote_desktop.py Flask endpoints:
 *   GET  /status   — server health check
 *   POST /landing  — handshake
 *   POST /receive  — encrypted credential delivery
 */

const STATUS_POLL_MS = 5000;

// ── DOM refs ──────────────────────────────────────────────────────────────
const badge       = document.getElementById('server-badge');
const serverIpEl  = document.getElementById('server-ip');
const logOutput   = document.getElementById('log-output');
const progressWrap= document.getElementById('progress-wrap');
const progressBar = document.getElementById('progress-bar');
const sendBtn     = document.getElementById('btn-send');
const clearBtn    = document.getElementById('btn-clear');
const keyInput    = document.getElementById('input-key');
const endpointInput = document.getElementById('input-endpoint');
const transportSel  = document.getElementById('input-transport');

// ── Logging ───────────────────────────────────────────────────────────────
function log(msg, type = 'default') {
  const now = new Date();
  const time = now.toTimeString().slice(0, 8);

  const line = document.createElement('div');
  line.className = `log-line ${type}`;
  line.innerHTML = `<span class="log-time">${time}</span><span class="log-msg">${msg}</span>`;
  logOutput.appendChild(line);
  logOutput.scrollTop = logOutput.scrollHeight;
}

// ── Progress ──────────────────────────────────────────────────────────────
function setProgress(pct) {
  if (pct === 0) {
    progressWrap.classList.remove('visible');
    progressBar.style.width = '0%';
    return;
  }
  progressWrap.classList.add('visible');
  progressBar.style.width = `${pct}%`;
}

// ── Server status poll ────────────────────────────────────────────────────
async function pollStatus() {
  try {
    const res  = await fetch('/status', { cache: 'no-store' });
    const data = await res.json();

    badge.textContent = '● ONLINE';
    badge.className   = 'online';

    if (data.ip && serverIpEl) {
      serverIpEl.textContent = data.ip;
    }
  } catch {
    badge.textContent = '● OFFLINE';
    badge.className   = 'offline';
  }
}

// ── Handshake ─────────────────────────────────────────────────────────────
async function sendHandshake(endpoint, keyHash) {
  log('Establishing landing zone...', 'info');
  setProgress(20);

  const res = await fetch(`${endpoint}/landing`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ handshake: true, key_hash: keyHash }),
  });

  if (!res.ok) throw new Error(`Landing failed: ${res.status}`);
  log('Landing zone confirmed.', 'ok');
  setProgress(50);
}

// ── Transmit ──────────────────────────────────────────────────────────────
async function transmitCredential(endpoint, encrypted) {
  log('Transmitting encrypted credential...', 'info');
  setProgress(75);

  const res = await fetch(`${endpoint}/receive`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ encrypted }),
  });

  if (!res.ok) throw new Error(`Transmission failed: ${res.status}`);
  log('Credential received by server.', 'ok');
  setProgress(100);
}

// ── Simple client-side hash (SHA-256 via Web Crypto) ─────────────────────
async function sha256hex(str) {
  const buf    = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}

// ── Simple XOR encode (placeholder — real encrypt happens server-side) ───
function clientEncode(str) {
  return btoa(unescape(encodeURIComponent(str)));
}

// ── Send flow ─────────────────────────────────────────────────────────────
async function handleSend() {
  const keyValue  = keyInput.value.trim();
  const endpoint  = endpointInput.value.trim().replace(/\/$/, '');
  const transport = transportSel.value;

  if (!keyValue) { log('No credential key provided.', 'warn'); return; }
  if (!endpoint) { log('No endpoint specified.', 'warn');        return; }

  sendBtn.disabled = true;
  setProgress(5);

  log(`Transport: ${transport.toUpperCase()}`, 'info');
  log(`Target: ${endpoint}`);

  try {
    const keyHash  = await sha256hex(keyValue);
    const encoded  = clientEncode(keyValue);

    await sendHandshake(endpoint, keyHash);
    await transmitCredential(endpoint, encoded);

    log('Transmission complete.', 'ok');
  } catch (err) {
    log(`Error: ${err.message}`, 'warn');
    setProgress(0);
  } finally {
    sendBtn.disabled = false;
    setTimeout(() => setProgress(0), 1800);
  }
}

// ── Clear log ─────────────────────────────────────────────────────────────
function handleClear() {
  logOutput.innerHTML = '';
  log('Log cleared.', 'default');
}

// ── Init ──────────────────────────────────────────────────────────────────
sendBtn.addEventListener('click', handleSend);
clearBtn.addEventListener('click', handleClear);

pollStatus();
setInterval(pollStatus, STATUS_POLL_MS);

log('Dashboard initialised.', 'info');
log(`Polling server every ${STATUS_POLL_MS / 1000}s...`);