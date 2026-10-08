import {validateReceipt, compareReceipt, labels, summaryMarkdown} from './core.mjs';
const $ = id => document.getElementById(id);
let samples = [], selected = 0, receipt = null, result = null, isExample = false, generation = 0;
const descriptions = [
  ['The test catches the bug.', 'The calculator subtracts instead of adding. The check exits with a failure.'],
  ['The focused fix passes.', 'Addition is corrected. The test passes, and the watched files match that saved moment.'],
  ['A later edit makes the pass stale.', 'The calculator changes again. The old passing result no longer describes those files.'],
];

function navigate() {
  if (location.hash === '#main') return;
  const page = ['overview', 'compare', 'guide'].includes(location.hash.slice(1)) ? location.hash.slice(1) : 'overview';
  document.querySelectorAll('.page').forEach(el => el.hidden = el.id !== page);
  document.querySelectorAll('[data-page]').forEach(el => {
    if (el.dataset.page === page) el.setAttribute('aria-current', 'page'); else el.removeAttribute('aria-current');
  });
  $('page-name').textContent = {overview:'Overview', compare:'Check a receipt', guide:'Get started'}[page];
}
window.addEventListener('hashchange', navigate); navigate();
$('theme').addEventListener('click', () => {
  const dark = document.body.classList.toggle('dark');
  $('theme').textContent = dark ? 'Light theme' : 'Dark theme';
  $('theme').setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
});
function notice(text, error=false) { $('notice').textContent = text; $('notice').classList.toggle('error', error); }
function showDemo(index) {
  selected = index;
  const sample = samples[index];
  if (!sample) return;
  const comparison = compareReceipt(sample.receipt, sample.current);
  document.querySelectorAll('[data-demo]').forEach(el => { const on = Number(el.dataset.demo) === index; el.classList.toggle('selected', on); el.setAttribute('aria-pressed', String(on)); });
  $('demo-label').textContent = labels[comparison.state][0];
  $('demo-label').classList.toggle('good', comparison.state === 'current_passed');
  $('demo-title').textContent = descriptions[index][0];
  $('demo-description').textContent = descriptions[index][1];
  $('demo-exit').textContent = sample.receipt.exit_code;
  $('demo-count').textContent = comparison.watched;
  $('open-example').disabled = false;
}
document.querySelectorAll('[data-demo]').forEach(el => el.addEventListener('click', () => showDemo(Number(el.dataset.demo))));
fetch('demo.json').then(r => {if (!r.ok) throw Error(); return r.json();}).then(data => {
  if (!Array.isArray(data) || data.length !== 3) throw Error();
  data.forEach(s => validateReceipt(s.receipt)); samples = data; showDemo(0);
}).catch(() => { $('demo-label').textContent = 'Example unavailable'; $('demo-description').textContent = 'You can still open your own receipt in Check a receipt.'; });

function renderFiles() {
  const query = $('file-search').value.toLowerCase();
  const list = $('file-list'); list.replaceChildren();
  for (const path of Object.keys(receipt.before).filter(p => p.toLowerCase().includes(query))) {
    const row = document.createElement('div'); row.className = 'file-row';
    const name = document.createElement('code'); name.textContent = path;
    const state = document.createElement('span');
    state.textContent = result.state === 'not_compared' ? 'Not compared' : result.changes.includes(path) ? 'Changed / missing' : 'Matches before snapshot';
    row.append(name, state); list.append(row);
  }
  if (!list.childElementCount) list.textContent = 'No matching paths.';
}
function renderReceipt() {
  $('summary-preview').hidden = true;
  $('receipt-view').hidden = false;
  $('receipt-status').textContent = isExample ? 'SAVED DEMONSTRATION SNAPSHOT' : result.state === 'not_compared' ? 'RECEIPT LOADED' : 'COMPARED IN THIS BROWSER';
  $('receipt-status').classList.toggle('good', result.state === 'current_passed');
  $('receipt-title').textContent = labels[result.state][0];
  $('receipt-description').textContent = labels[result.state][1];
  $('recorded-outcome').textContent = receipt.check_status;
  $('watched-count').textContent = Object.keys(receipt.before).length;
  $('duration').textContent = receipt.duration_seconds + ' s';
  $('command').textContent = JSON.stringify(receipt.command, null, 2);
  $('started').textContent = 'Started: ' + receipt.started_at;
  $('exit-code').textContent = 'Recorded exit code: ' + (receipt.exit_code ?? 'none');
  $('folder-input').disabled = false; $('folder-label').classList.remove('disabled');
  renderFiles();
}
$('open-example').addEventListener('click', () => {
  generation++; receipt = samples[selected].receipt; result = compareReceipt(receipt, samples[selected].current); isExample = true;
  $('receipt-input').value = ''; $('folder-input').value = ''; $('file-search').value = '';
  renderReceipt(); notice('Example from a real local test. These saved snapshots do not describe your project.'); location.hash = 'compare';
});
$('receipt-input').addEventListener('change', async event => {
  const file = event.target.files[0]; if (!file) return;
  const token = ++generation;
  receipt = null; result = null; $('receipt-view').hidden = true; $('folder-input').disabled = true; $('folder-label').classList.add('disabled'); $('folder-input').value = '';
  try {
    if (file.size > 2 * 1024 * 1024) throw Error('Choose a receipt smaller than 2 MiB.');
    const parsed = validateReceipt(JSON.parse(await file.text()));
    if (token !== generation) return;
    receipt = parsed; result = {state:'not_compared', changes:[], watched:Object.keys(receipt.before).length}; isExample = false;
    $('file-search').value = ''; renderReceipt(); notice('Receipt loaded. Select the original project root folder to compare watched files.');
  } catch (error) { if (token === generation) notice(error.message || 'This receipt could not be opened.', true); }
});
$('folder-input').addEventListener('change', async event => {
  if (!receipt || !event.target.files.length) return;
  const token = ++generation, record = receipt;
  // Reset the previous result before any asynchronous work or potential error.
  isExample = false; result = {state:'not_compared',changes:[],watched:Object.keys(record.before).length}; renderReceipt();
  notice('Comparing selected files locally…');
  try {
    const files = new Map();
    for (const file of event.target.files) {
      const relative = file.webkitRelativePath.split('/').slice(1).join('/');
      if (relative && files.has(relative)) throw Error('The selected folder contains duplicate paths.');
      if (relative) files.set(relative, file);
    }
    let bytes = 0; const current = Object.create(null);
    for (const name of Object.keys(record.before)) {
      if (token !== generation) return;
      const file = files.get(name);
      if (!file) { current[name] = null; continue; }
      bytes += file.size;
      if (bytes > 64 * 1024 * 1024) throw Error('Watched files exceed the 64 MiB comparison limit.');
      const hash = await crypto.subtle.digest('SHA-256', await file.arrayBuffer());
      current[name] = Array.from(new Uint8Array(hash), b => b.toString(16).padStart(2, '0')).join('');
    }
    if (token !== generation) return;
    result = compareReceipt(record, current); renderReceipt();
    notice('Comparison complete. This is a snapshot of your selected files. Select the folder again after further edits. No files were uploaded.');
  } catch (error) { if (token === generation) notice(error.message || 'Files could not be compared.', true); }
  event.target.value = '';
});
$('file-search').addEventListener('input', () => { if (receipt) renderFiles(); });
$('export').addEventListener('click', () => {
  if (!receipt) return;
  const summary = summaryMarkdown(receipt, result, isExample);
  $('summary-text').textContent = summary; $('summary-preview').hidden = false; $('summary-preview').open = true;
  const url = URL.createObjectURL(new Blob([summary], {type:'text/markdown;charset=utf-8'}));
  const link = document.createElement('a'); link.href = url; link.download = 'patchproof-summary.md'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  notice('Summary download requested. A copyable preview is shown below. Review its command arguments and filenames before sharing.');
});
$('copy-prompt').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText($('prompt').textContent); $('copy-notice').textContent = 'Copied. Paste this into Codex with your project open.'; }
  catch { $('copy-notice').textContent = 'Copy is unavailable here. Select and copy the prompt above.'; }
});
