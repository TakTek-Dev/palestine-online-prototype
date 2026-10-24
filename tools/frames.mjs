// Frames of the first call (the first-visit loader) through Chrome DevTools Protocol.
// node --experimental-websocket tools/frames.mjs <url> <out-prefix> [width] [height] [ms,ms,...]
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [url, out, w = '1440', h = '900', times = '150,450,800,1100,1400,2200', scheme = 'light'] = process.argv.slice(2);
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const port = 9300 + Math.floor(Math.random() * 400);
const proc = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), 'cp-frames-'))}`, '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
try {
  let target;
  for (let k = 0; k < 50 && !target; k++) { try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === 'page'); } catch {} await sleep(150); }
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); } });
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: +w, height: +h, deviceScaleFactor: 1, mobile: +w < 768 });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: scheme }] });
  // warm the cache first so fonts and photos are ready, as on a second page view
  await send('Page.navigate', { url: url.replace('?loader', '') }); await sleep(6000);
  await send('Runtime.evaluate', { expression: "sessionStorage.clear()" });
  const t0 = Date.now();
  await send('Page.navigate', { url });
  for (const [i, t] of times.split(',').map(Number).entries()) {
    const wait = t - (Date.now() - t0); if (wait > 0) await sleep(wait);
    const st = await send('Runtime.evaluate', { expression: "JSON.stringify([performance.now()|0, document.documentElement.className, (document.getElementById('loader')||{}).className, JSON.stringify(document.getElementById('loader').getBoundingClientRect()), (document.elementFromPoint(720,450)||{}).className, getComputedStyle(document.getElementById('loader')).backgroundColor, getComputedStyle(document.getElementById('loader')).opacity])", returnByValue: true });
    console.log(i, st.result.value);
    const shot = await send('Page.captureScreenshot', { format: 'png' });
    writeFileSync(`${out}-${i}.png`, Buffer.from(shot.data, 'base64'));
  }
  console.log('frames', times);
} finally { try { ws && ws.close(); } catch {} proc.kill(); }
