/**
 * Serveur gratuit du CRM Maison Tinado, dans Google Sheets (Apps Script).
 * Installation : voir LISEZMOI. Le code d'accès se règle ci-dessous.
 */
const CODE_ACCES = "CHANGER-MOI";
const COLS = ["reservations", "contacts", "commandes", "activite"];

function sheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName("donnees");
  if (!sh) { sh = ss.insertSheet("donnees"); sh.appendRow(["collection", "id", "contenu", "maj"]); sh.setFrozenRows(1); }
  return sh;
}
function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function version_() { return Number(PropertiesService.getScriptProperties().getProperty("v") || 0); }
function bump_() { PropertiesService.getScriptProperties().setProperty("v", String(version_() + 1)); }

function doGet() { return out_({ ok: true, service: "CRM Maison Tinado" }); }
function doPost(e) {
  let b; try { b = JSON.parse(e.postData.contents); } catch (x) { return out_({ error: "bad" }); }
  if (b.code !== CODE_ACCES) return out_({ error: "auth" });
  if (b.action === "login") return out_({ ok: true });
  if (b.action === "version") return out_({ v: version_() });
  const sh = sheet_();
  if (b.action === "all") {
    const rows = sh.getDataRange().getValues().slice(1), data = { reservations: [], contacts: [], commandes: [], activite: [] };
    rows.forEach(r => { if (data[r[0]]) { try { data[r[0]].push(Object.assign({ id: String(r[1]) }, JSON.parse(r[2]))); } catch (x) {} } });
    data.activite.sort((a, b) => b.le - a.le); data.activite = data.activite.slice(0, 300);
    return out_({ data: data, v: version_() });
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
