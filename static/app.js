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
  if (tpl && tpl.content && tpl.content.firstElementChild) {
    const node = tpl.content.firstElementChild.cloneNode(true);
    node.textContent = msg;
    document.body.appendChild(node);
    setTimeout(() => node.remove(), timeout);
  } else {
    // minimal fallback
    console.warn('Toast:', msg);
  }
}

function setProcessState(on){
  const btn = qs('#processBtn');
  if (!btn) return;
  btn.classList.toggle('state-on', on);
  btn.classList.toggle('state-off', !on);
  btn.setAttribute('aria-pressed', String(on));
  isDirty = !on;
}

function getSelectionErrors(){
  const errors = [];
  if (!selections.class || selections.class.size === 0) errors.push("You must select at least one class");
  if (!selections.archetype || selections.archetype.size === 0) errors.push("You must select at least one archetype");
  if (!selections.set || selections.set.size === 0) errors.push("You must select at least one set");
  return errors;
}

function applyProcessInvalidVisual(btn, blocked){
  if(!btn) return;
  let icon = btn.querySelector('.check');
  let textSpan = btn.querySelector('.btn-text');
  // Ensure children exist in a non-destructive way
  if(!textSpan){
    textSpan = document.createElement('span');
    textSpan.className = 'btn-text';
    textSpan.textContent = btn.textContent.trim() || 'Process';
    btn.textContent = '';
    btn.appendChild(textSpan);
  }
  if(!icon){
    icon = document.createElement('span');
    icon.className = 'check';
    btn.insertBefore(icon, textSpan);
  }
  if(blocked){
    btn.classList.add('invalid');
    btn.disabled = true;
    btn.setAttribute('aria-disabled','true');
    // Force visuals inline so they can't be overridden
    btn.style.borderColor = 'var(--error)';
    btn.style.color = 'var(--error)';
    btn.style.opacity = '1';
    btn.style.filter = 'none';
    btn.style.boxShadow = 'none';
    icon.style.display = 'inline-block';
    textSpan.textContent = "You must select at least one Class, Archetype, and Set";
  } else {
    btn.classList.remove('invalid');
    btn.removeAttribute('aria-disabled');
    // remove inline overrides
    btn.style.removeProperty('border-color');
    btn.style.removeProperty('color');
    btn.style.removeProperty('opacity');
    btn.style.removeProperty('filter');
    btn.style.removeProperty('box-shadow');
    icon.style.display = 'none';
    textSpan.textContent = "Process";
  }
}

function updateProcessEnabled(){
  const btn = qs('#processBtn');
  if(!btn) return;
  const errs = getSelectionErrors();
  const blocked = errs.length > 0;
  btn.disabled = blocked;
  btn.setAttribute('aria-disabled', String(blocked));
  applyProcessInvalidVisual(btn, blocked);
}

/* File handling --------------------------------------------- */
function validateFile(f){
  if(!f) return { ok:false, reason: "No file selected" };
  if(f.name !== REQUIRED_FILENAME){
    return { ok:false, reason: `Invalid filename. Must be "${REQUIRED_FILENAME}".` };
  }
  if(f.size > MAX_FILE_BYTES){
    return { ok:false, reason: `File too large (${Math.ceil(f.size/1024)}KB). Max is 500KB.` };
  }
  return { ok:true };
}

function attachFileHandlers(){
  const drop = qs('#fileDrop');
  const input = qs('#fileInput');

  function onFilePicked(f){
    const verdict = validateFile(f);
    if(!verdict.ok){
      file = null;
      showToast(`❌ ${verdict.reason}`);
      drop && drop.classList.remove('ok');
      // restore original inside-box text
      const t = window.originalFileBox || {};
      if(qs('#fileBoxTitle')) qs('#fileBoxTitle').textContent = t.title || qs('#fileBoxTitle').textContent;
      if(qs('#fileBoxSub'))   qs('#fileBoxSub').textContent   = t.sub   || qs('#fileBoxSub').textContent;
      if(qs('#fileBoxNote'))  qs('#fileBoxNote').innerHTML    = t.note  || qs('#fileBoxNote').innerHTML;
      setProcessState(false);
      updateProcessEnabled();
      return;
    }
    file = f;
    // Ready message inside the box
    const kb = Math.ceil(file.size/1024);
    if(qs('#fileBoxTitle')) qs('#fileBoxTitle').textContent = `Ready: ${file.name} (${kb}KB)`;
    if(qs('#fileBoxSub'))   qs('#fileBoxSub').textContent   = '';
    if(qs('#fileBoxNote'))  qs('#fileBoxNote').innerHTML    = '';
    drop && drop.classList.add('ok');
    setProcessState(false); // mark dirty
    updateProcessEnabled();
  }

  // Click-to-pick
  input && input.addEventListener('change', (e) => {
    const f = e.target.files && e.target.files[0];
    if(f) onFilePicked(f);
  });

  if(!drop) return;

  // Drag & Drop UX
  ['dragenter','dragover'].forEach(evt => {
    drop.addEventListener(evt, e => {
      e.preventDefault(); e.stopPropagation();
      drop.classList.add('dragover');
    });
  });
  ['dragleave','drop'].forEach(evt => {
    drop.addEventListener(evt, e => {
      e.preventDefault(); e.stopPropagation();
      drop.classList.remove('dragover');
    });
  });
  drop.addEventListener('drop', e => {
    const f = e.dataTransfer.files && e.dataTransfer.files[0];
    if(f) onFilePicked(f);
  });
  // Keyboard support
  drop.addEventListener('keydown', (e) => {
    if(e.key === 'Enter' || e.key === ' '){
      e.preventDefault();
      input && input.click();
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
      updateProcessEnabled();
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
      updateProcessEnabled();
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
        await navigator.clipboard.writeText(el.value || '');
        showToast('Copied to clipboard');
      } catch(err){
        if (el && el.select) {
          el.select();
          document.execCommand('copy');
          showToast('Copied (fallback)');
        }
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
  const selErrs = getSelectionErrors();
  if(selErrs.length){
    selErrs.forEach(e => showToast(e));
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
  const btn = qs('#processBtn');
  if (btn) btn.addEventListener('click', processNow);
}

/* Mobile-only accordion ------------------------------------- */
function attachMobileAccordion(){
  const mq = window.matchMedia('(max-width: 720px)');
  const bars = ['#classBar', '#setBar', '#archetypeBar'];

  function enableMobile(){
    bars.forEach(sel => {
      const bar = qs(sel);
      if(!bar) return;
      const col = bar.closest('.sel-col');
      if(!col) return;

      // Start collapsed by default on mobile
      col.classList.add('collapsed');
      bar.setAttribute('aria-expanded','false');
      bar.setAttribute('role','button');
      bar.setAttribute('tabindex','0');

      if(bar.__accordionBound) return;
      const toggle = () => {
        const c = col.classList.toggle('collapsed');
        bar.setAttribute('aria-expanded', String(!c));
      };
      bar.addEventListener('click', toggle);
      bar.addEventListener('keydown', (e) => {
        if(e.key === 'Enter' || e.key === ' '){
          e.preventDefault(); toggle();
        }
      });
      bar.__accordionBound = true;
    });
  }

  function disableDesktop(){
    document.querySelectorAll('.sel-col').forEach(col => col.classList.remove('collapsed'));
    bars.forEach(sel => {
      const bar = qs(sel);
      if(bar) bar.setAttribute('aria-expanded','true');
    });
  }

  if(mq.matches) enableMobile(); else disableDesktop();

  if (mq.addEventListener) {
    mq.addEventListener('change', (e) => {
      if(e.matches) enableMobile();
      else disableDesktop();
    });
  } else {
    // Fallback
    window.addEventListener('resize', () => {
      const isMobile = window.matchMedia('(max-width: 720px)').matches;
      if(isMobile) enableMobile(); else disableDesktop();
    });
  }
}

/* Init ------------------------------------------------------ */
function init(){
  // Cache original dropbox text to preserve until a valid file is uploaded
  window.originalFileBox = {
    title: (qs('#fileBoxTitle')?.textContent || ""),
    sub:   (qs('#fileBoxSub')?.textContent || ""),
    note:  (qs('#fileBoxNote')?.innerHTML || "")
  };

  attachFileHandlers();
  attachSelectionHandlers();
  attachCopyHandlers();
  attachProcessHandler();
  attachMobileAccordion();

  // Preselect default tier (visual + state)
  const defaultBtn = document.querySelector(`.tier-card[data-value="${DEFAULT_TIER}"]`);
  if (defaultBtn) {
    qsa('.tier-card').forEach(b => b.classList.remove('on'));
    defaultBtn.classList.add('on');
    selections.tier = DEFAULT_TIER;
  }

  setProcessState(false); // initial state: needs run
  updateProcessEnabled(); // reflect invalid state on first load
}

document.addEventListener('DOMContentLoaded', init);
