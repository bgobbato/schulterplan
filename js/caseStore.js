/* IndexedDB-backed store for imported planning_package cases.

   The MPR planner accepts a planning_package.zip dropped by the surgeon and
   has to share that case across three pages (scapula planner, humerus
   planner, dashboard). Plain JS memory disappears on navigation, and
   localStorage is too small for the ~64 MB CT NIfTI, so the case (payload +
   meshes + CT volume) lives in IndexedDB.

   One record per caseId — the most recent import always wins on re-import.
   localStorage carries a one-line `active_case` flag so a page can short-
   circuit when no case is imported. */

const DB_NAME = 'schulterplan';
const DB_VERSION = 1;
const STORE = 'cases';
const ACTIVE_KEY = 'schulterplan_active_case';

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE, { keyPath: 'caseId' });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror   = () => reject(req.error);
  });
}

function objectStore(db, mode) {
  return db.transaction(STORE, mode).objectStore(STORE);
}

/* Save (or overwrite) a case. Pass an object with:
   { caseId, payload, scapulaObj, humerusObj?, niftiBuffer? } */
export async function saveCase(record) {
  if (!record || !record.caseId) throw new Error('saveCase: caseId required');
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const r = objectStore(db, 'readwrite').put({ ...record, savedAt: Date.now() });
    r.onsuccess = () => resolve();
    r.onerror   = () => reject(r.error);
  });
}

export async function loadCase(caseId) {
  if (!caseId) return null;
  try {
    const db = await openDB();
    return await new Promise((resolve, reject) => {
      const r = objectStore(db, 'readonly').get(caseId);
      r.onsuccess = () => resolve(r.result || null);
      r.onerror   = () => reject(r.error);
    });
  } catch (e) {
    console.warn('[caseStore] loadCase failed:', e);
    return null;
  }
}

export async function loadActiveCase() {
  const id = getActiveCaseId();
  if (!id) return null;
  return loadCase(id);
}

export function getActiveCaseId() {
  try { return localStorage.getItem(ACTIVE_KEY); } catch (_) { return null; }
}

export function setActiveCase(caseId) {
  try {
    if (caseId) localStorage.setItem(ACTIVE_KEY, caseId);
    else        localStorage.removeItem(ACTIVE_KEY);
  } catch (_) { /* private mode etc. */ }
}

export function clearActiveCase() {
  setActiveCase(null);
}

export async function deleteCase(caseId) {
  if (!caseId) return;
  try {
    const db = await openDB();
    await new Promise((resolve, reject) => {
      const r = objectStore(db, 'readwrite').delete(caseId);
      r.onsuccess = () => resolve();
      r.onerror   = () => reject(r.error);
    });
  } catch (e) { console.warn('[caseStore] deleteCase failed:', e); }
}

/* Convenience: build a Blob URL from a stored binary/text mesh field.
   Caller is responsible for revoking. */
export function blobUrlFromText(text, type = 'text/plain') {
  return URL.createObjectURL(new Blob([text], { type }));
}

export function blobUrlFromBuffer(buffer, type = 'application/octet-stream') {
  return URL.createObjectURL(new Blob([buffer], { type }));
}
