export const labels = {
  current_passed: ['Check passed · files match', 'The selected command exited zero and the selected file bytes match the receipt.'],
  current_failed: ['Check failed · files match', 'The command failed. These files still match that recorded run.'],
  current_error: ['Check could not start', 'The recorded command did not start successfully.'],
  current_timed_out: ['Check timed out', 'The recorded command exceeded its time limit.'],
  changed_since_check: ['Result is out of date', 'A watched file changed or is missing. Run the check again before relying on the earlier result.'],
  changed_during_check: ['Files changed during the check', 'The before and after fingerprints differ. Review the changes and run the check again.'],
  snapshot_unavailable: ['Files could not be rechecked', 'The receipt has no after-check snapshot. It cannot establish matching inputs.'],
  not_compared: ['Files not compared yet', 'This receipt records a past run. Select the project folder to compare its watched files now.'],
};

export function validateReceipt(value) {
  const object = v => v && typeof v === 'object' && !Array.isArray(v);
  if (!object(value) || value.schema_version !== 1 || !['passed', 'failed', 'error', 'timed_out'].includes(value.check_status)) throw Error('Choose a PatchProof version 1 receipt JSON file.');
  if (!Array.isArray(value.command) || !value.command.length || value.command.length > 256 || !value.command.every(v => typeof v === 'string' && v.length <= 16384)) throw Error('This receipt has an invalid command.');
  if (!object(value.before)) throw Error('This receipt has no watched-file fingerprints.');
  const paths = Object.keys(value.before);
  if (!paths.length || paths.length > 2000) throw Error('Receipts must watch between 1 and 2,000 files.');
  const hash = v => typeof v === 'string' && /^[a-f0-9]{64}$/.test(v);
  for (const path of paths) {
    if (!path || /[\\:\x00-\x1f]/.test(path) || path.split('/').some(p => !p || p === '.' || p === '..') || !hash(value.before[path])) throw Error('This receipt contains an invalid watched path or fingerprint.');
  }
  if (value.after !== null && (!object(value.after) || Object.keys(value.after).length !== paths.length || !paths.every(p => Object.hasOwn(value.after, p) && (value.after[p] === null || hash(value.after[p]))))) throw Error('The after-check snapshot is invalid.');
  if (value.check_status === 'passed' && value.exit_code !== 0) throw Error('A passed check must have exit code zero.');
  if (value.exit_code !== null && !Number.isInteger(value.exit_code)) throw Error('The exit code is invalid.');
  if (typeof value.started_at !== 'string' || !Number.isFinite(Date.parse(value.started_at)) || !Number.isFinite(value.duration_seconds) || value.duration_seconds < 0) throw Error('The receipt timing is invalid.');
  return value;
}

export function compareReceipt(receipt, current) {
  validateReceipt(receipt);
  const paths = Object.keys(receipt.before);
  const changes = paths.filter(p => !Object.hasOwn(current, p) || current[p] !== receipt.before[p]);
  let state;
  if (receipt.after === null) state = 'snapshot_unavailable';
  else if (paths.some(p => receipt.before[p] !== receipt.after[p])) state = 'changed_during_check';
  else if (changes.length) state = 'changed_since_check';
  else state = 'current_' + receipt.check_status;
  return {state, changes, watched: paths.length};
}

export function summaryMarkdown(receipt, result, example = false) {
  const safe = v => String(v).replace(/[\r\n]/g, ' ');
  return `# PatchProof check summary\n\n${example ? 'Saved demonstration snapshot; not a current project check.\n\n' : ''}Status: ${labels[result.state][0]}\n\nRecorded command arguments: ${JSON.stringify(receipt.command)}\n\nStarted: ${safe(receipt.started_at)}\nExit code: ${receipt.exit_code ?? 'none'}\nDuration: ${receipt.duration_seconds} seconds\n\nWatched files:\n${Object.keys(receipt.before).map(p => '- ' + safe(p)).join('\n')}\n\n${result.changes.length ? 'Changed or missing files:\n' + result.changes.map(p => '- ' + safe(p)).join('\n') + '\n\n' : ''}Only listed files were considered. Unwatched files, dependency installations, environment changes, and changes restored between snapshots are outside this check. Receipts are editable, unsigned records. A passing command does not prove correctness, coverage, or security. This exported report is a snapshot and does not update automatically.\n`;
}
