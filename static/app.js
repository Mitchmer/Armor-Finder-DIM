/* Config ---------------------------------------------------- */
const MAX_FILE_BYTES = 500 * 1024; // 500 KB
const REQUIRED_FILENAME = "destiny-armor.csv";
const PROCESS_URL = "/process"; // Flask endpoint (POST)
const DEFAULT_TIER = "3";

/* State ----------------------------------------------------- */
let file = null;
let isDirty = true; // selections/file changed since last successful run

const selections = {
  class: new Set(),
  archetype: new Set(),
  set: new Set(),
  tier: null,
};

/* Helpers --------------------------------------------------- */
const qs  = (s, el = document) => el.querySelector(s);
const qsa = (s, el = document) => Array.from(el.querySelectorAll(s));

function showToast(msg, timeout = 2200){
  const tpl = qs('#toastTpl');
  const node = tpl.content.firstElementChild.cloneNode(true);
  node.textContent = msg;
  document.body.appendChild(node);
  setTimeout(() => node.remove(), timeout);
}

function setProcessState(on){
  const btn = qs('#processBtn');
  btn.classList.toggle('state-on', on);
  btn.classList.toggle('state-off', !on);
  btn.setAttribute('aria-pressed', String(on));
  isDirty = !on;
}

/* File handling --------------------------------------------- */
function validateFile(f){
  if(!f) return { ok:false, reason: "No file selected" };
  if(f.name !== REQUIRED_FILENAME){
    return { ok:false, reason: `Invalid file. Must be "${REQUIRED_FILENAME}".` };
  }
  if(f.size > MAX_FILE_BYTES){
    return { ok:false, reason: `File too large (${Math.ceil(f.size/1024)}KB). Max is 500KB.` };
  }
  return { ok:true };
}

function attachFileHandlers(){
  const drop = qs('#fileDrop');
  const input = qs('#fileInput');
  const status = qs('#fileStatus');

  function onFilePicked(f){
    const { ok, reason } = validateFile(f);
    if(!ok){
      file = null;
      status.textContent = `❌ ${reason}`;
      setProcessState(false);
      return;
    }
    file = f;
    status.textContent = `✅ Ready: ${file.name} (${Math.ceil(f.size/1024)}KB)`;
    setProcessState(false); // mark dirty
  }

  // Click-to-pick
  input.addEventListener('change', (e) => {
    const f = e.target.files?.[0];
    if(f) onFilePicked(f);
  });

  // Drag & Drop UX
  ;['dragenter','dragover'].forEach(evt => {
    drop.addEventListener(evt, e => {
      e.preventDefault(); e.stopPropagation();
      drop.classList.add('dragover');
    });
  });
  ;['dragleave','drop'].forEach(evt => {
    drop.addEventListener(evt, e => {
      e.preventDefault(); e.stopPropagation();
      drop.classList.remove('dragover');
    });
  });
  drop.addEventListener('drop', e => {
    const f = e.dataTransfer.files?.[0];
    if(f) onFilePicked(f);
  });
  // Keyboard support
  drop.addEventListener('keydown', (e) => {
    if(e.key === 'Enter' || e.key === ' '){
      e.preventDefault();
      input.click();
    }
  });
}

/* Selection toggles ----------------------------------------- */
function attachSelectionHandlers(){
  // Multi-choice for class/archetype/set
  qsa('.toggle-card').forEach(btn => {
    const group = btn.dataset.group;
    if (group === 'tier') return; // handled below
    btn.addEventListener('click', () => {
      const value = btn.dataset.value;
      btn.classList.toggle('on');
      if(btn.classList.contains('on')){
        selections[group].add(value);
      } else {
        selections[group].delete(value);
      }
      setProcessState(false);
    });
  });

  // Single-choice for tier (radio behavior)
  qsa('.tier-card').forEach(btn => {
    btn.addEventListener('click', () => {
      // turn all off, then turn this on
      qsa('.tier-card').forEach(b => b.classList.remove('on'));
      btn.classList.add('on');
      selections.tier = btn.dataset.value;
      setProcessState(false);
    });
  });
}

/* Copy buttons ---------------------------------------------- */
function attachCopyHandlers(){
  qsa('.copy-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const targetSel = btn.getAttribute('data-target');
      const el = qs(targetSel);
      try{
        await navigator.clipboard.writeText(el.value);
        showToast('Copied to clipboard');
      } catch(err){
        // Fallback
        el.select();
        document.execCommand('copy');
        showToast('Copied (fallback)');
      }
    });
  });
}

/* Process action -------------------------------------------- */
async function processNow(){
  const btn = qs('#processBtn');

  if(!file){
    showToast('Please choose destiny-armor.csv first');
    return;
  }
  if(!selections.tier){
    showToast('Please select a minimum tier');
    return;
  }

  btn.disabled = true;

  const form = new FormData();
  form.append('file', file);
  form.append('class', JSON.stringify(Array.from(selections.class)));
  form.append('archetype', JSON.stringify(Array.from(selections.archetype)));
  form.append('set', JSON.stringify(Array.from(selections.set)));
  form.append('tier', selections.tier);

  try{
    const res = await fetch(PROCESS_URL, { method: 'POST', body: form });
    if(!res.ok){
      throw new Error(`Server error: ${res.status}`);
    }
    const data = await res.json();
    const top = data.resultTop ?? data.result ?? "";
    const bottom = data.resultBottom ?? "";

    qs('#outputTop').value = top;
    qs('#outputBottom').value = bottom;

    setProcessState(true); // processed & up-to-date
    showToast('Processed successfully');
  } catch(err){
    console.error(err);
    showToast(err.message || 'Failed to process');
  } finally {
    btn.disabled = false;
  }
}

function attachProcessHandler(){
  qs('#processBtn').addEventListener('click', processNow);
}

/* Init ------------------------------------------------------ */
function init(){
  attachFileHandlers();
  attachSelectionHandlers();
  attachCopyHandlers();
  attachProcessHandler();

  // Preselect default tier (visual + state)
  const defaultBtn = document.querySelector(`.tier-card[data-value="${DEFAULT_TIER}"]`);
  if (defaultBtn) {
    qsa('.tier-card').forEach(b => b.classList.remove('on'));
    defaultBtn.classList.add('on');
    selections.tier = DEFAULT_TIER;
  }

  setProcessState(false); // initial state: needs run
}

document.addEventListener('DOMContentLoaded', init);
