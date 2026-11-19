/**
 * Serveur gratuit du CRM YOKK, dans Google Sheets (Apps Script).
 * Installation : voir LISEZMOI. Le code d'accès de l'équipe se règle ci-dessous.
 */
const CODE_ACCES = "CHANGER-MOI";
const COLS = ["prospects", "taches", "activite"];

function sheet_() {
  let ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) {
    const p = PropertiesService.getScriptProperties(), id = p.getProperty("sheetId");
    ss = id ? SpreadsheetApp.openById(id) : SpreadsheetApp.create("YOKK - CRM");
    if (!id) p.setProperty("sheetId", ss.getId());
  }
  let sh = ss.getSheetByName("donnees");
  if (!sh) { sh = ss.insertSheet("donnees"); sh.appendRow(["collection", "id", "contenu", "maj"]); sh.setFrozenRows(1); }
  return sh;
}
function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function props_() { return PropertiesService.getScriptProperties(); }
function version_() { return Number(props_().getProperty("v") || 0); }
function bump_() { props_().setProperty("v", String(version_() + 1)); }
function membres_() { try { return JSON.parse(props_().getProperty("membres") || "[]"); } catch (x) { return []; } }

/* Présence en direct : qui est connecté et ce qu'il consulte (gardé 2 minutes) */
function presence_(nom, pr) {
  const c = CacheService.getScriptCache(); let m = {};
  try { m = JSON.parse(c.get("presence") || "{}"); } catch (x) {}
  const now = Date.now();
  if (nom) m[nom] = { by: nom, presence: pr || {}, updatedAt: now };
  Object.keys(m).forEach(k => { if (now - m[k].updatedAt > 120000) delete m[k]; });
  c.put("presence", JSON.stringify(m), 600);
  return Object.keys(m).map(k => m[k]);
}

function doGet() { return out_({ ok: true, service: "CRM YOKK" }); }
function doPost(e) {
  try { return handle_(e); } catch (err) { return out_({ error: "server", message: String(err) }); }
}
function handle_(e) {
  let b; try { b = JSON.parse(e.postData.contents); } catch (x) { return out_({ error: "bad" }); }
  if (b.code !== CODE_ACCES) return out_({ error: "auth" });
  const nom = String(b.nom || "").slice(0, 40);
  if (b.action === "login") {
    const m = membres_(); if (nom && m.indexOf(nom) < 0) { m.push(nom); props_().setProperty("membres", JSON.stringify(m)); }
    return out_({ ok: true });
  }
  if (b.action === "version" || b.action === "ping") {
    const peers = b.action === "ping" ? presence_(nom, b.presence) : presence_(null);
    return out_({ v: version_(), peers: peers, membres: membres_() });
  }
  const sh = sheet_();
  if (b.action === "all") {
    const rows = sh.getDataRange().getValues().slice(1), data = { prospects: [], taches: [], activite: [] };
    rows.forEach(r => { if (data[r[0]]) { try { data[r[0]].push(Object.assign({ id: String(r[1]) }, JSON.parse(r[2]))); } catch (x) {} } });
    data.activite.sort((a, b) => b.le - a.le); data.activite = data.activite.slice(0, 400);
    return out_({ data: data, v: version_(), peers: presence_(null), membres: membres_() });
  }
  if (COLS.indexOf(b.col) < 0 || !/^[A-Za-z0-9_-]{1,64}$/.test(String(b.id))) return out_({ error: "bad" });
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    const ids = sh.getRange(1, 1, sh.getLastRow(), 2).getValues();
    let row = -1; for (let i = 1; i < ids.length; i++) if (ids[i][0] === b.col && String(ids[i][1]) === String(b.id)) { row = i + 1; break; }
    if (b.action === "put") {
      const vals = [[b.col, String(b.id), JSON.stringify(b.data || {}), new Date()]];
      if (row > 0) sh.getRange(row, 1, 1, 4).setValues(vals); else sh.appendRow(vals[0]);
    } else if (b.action === "del") { if (row > 0) sh.deleteRow(row); }
    else return out_({ error: "bad" });
    bump_();
  } finally { lock.releaseLock(); }
  return out_({ ok: true });
}
