// Console errors, failed requests and horizontal overflow for a page at a width.
// node --experimental-websocket tools/errs.mjs <url> [width]
import { spawn } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
const [url, w = '390'] = process.argv.slice(2);
const port = 9700 + Math.floor(Math.random() * 200);
const proc = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), 'cp-err-'))}`, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map(); const out = [];
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
try {
  let t; for (let k = 0; k < 50 && !t; k++) { try { t = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((x) => x.type === 'page'); } catch {} await sleep(150); }
  ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
    if (m.method === 'Runtime.exceptionThrown') out.push('EXC ' + m.params.exceptionDetails.exception?.description);
    if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type)) out.push(m.params.type + ' ' + m.params.args.map((a) => a.value).join(' '));
    if (m.method === 'Network.loadingFailed') out.push('FAIL ' + m.params.errorText);
    if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) out.push(m.params.response.status + ' ' + m.params.response.url); });
  await send('Runtime.enable'); await send('Network.enable'); await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: +w, height: 844, deviceScaleFactor: 1, mobile: +w < 768 });
  await send('Page.navigate', { url }); await sleep(3500);
  const H = JSON.parse((await send('Runtime.evaluate', { expression: 'JSON.stringify(document.documentElement.scrollHeight)', returnByValue: true })).result.value);
  for (let y = 0; y < H; y += 700) { await send('Runtime.evaluate', { expression: `scrollTo(0,${y})` }); await sleep(60); }
  await sleep(800);
  const r = await send('Runtime.evaluate', { expression: `JSON.stringify({sw:document.documentElement.scrollWidth,cw:innerWidth,h:document.documentElement.scrollHeight,wide:[...document.querySelectorAll('body *')].filter(e=>{const b=e.getBoundingClientRect();return b.width&&b.right>innerWidth+1&&!e.closest('.nav ul')}).slice(0,5).map(e=>e.tagName+'.'+e.className)})`, returnByValue: true });
  console.log(url, w, r.result.value, out.length ? '\n' + out.join('\n') : 'no errors');
} finally { try { ws.close(); } catch {} proc.kill(); }
