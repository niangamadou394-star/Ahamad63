// CRM Maison Tinado : serveur Express + PostgreSQL (fichier JSON en local si DATABASE_URL est absent)
const express = require("express");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 3000;
const CODE = process.env.ACCESS_CODE || "tinado";            // code d'accès partagé
const SECRET = process.env.SESSION_SECRET || crypto.randomBytes(32).toString("hex");
const COLS = new Set(["reservations", "contacts", "commandes", "activite"]);

/* ---------- stockage ---------- */
let store;
if (process.env.DATABASE_URL) {
  const { Pool } = require("pg");
  const pool = new Pool({ connectionString: process.env.DATABASE_URL, ssl: process.env.PGSSL === "off" ? false : { rejectUnauthorized: false } });
  store = {
    init: () => pool.query(`CREATE TABLE IF NOT EXISTS docs (col TEXT NOT NULL, id TEXT NOT NULL, data JSONB NOT NULL, updated BIGINT NOT NULL, PRIMARY KEY (col, id))`),
    all: async () => (await pool.query("SELECT col, id, data, updated FROM docs")).rows,
    put: (col, id, data) => pool.query("INSERT INTO docs (col,id,data,updated) VALUES ($1,$2,$3,$4) ON CONFLICT (col,id) DO UPDATE SET data=$3, updated=$4", [col, id, data, Date.now()]),
    del: (col, id) => pool.query("DELETE FROM docs WHERE col=$1 AND id=$2", [col, id]),
    version: async () => Number((await pool.query("SELECT COALESCE(MAX(updated),0) v FROM docs")).rows[0].v) + Number((await pool.query("SELECT COUNT(*) c FROM docs")).rows[0].c),
  };
} else {
  const file = path.join(__dirname, "data.json");
  let rows = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf8")) : [];
  const save = () => fs.writeFileSync(file, JSON.stringify(rows));
  store = {
    init: async () => {},
    all: async () => rows,
    put: async (col, id, data) => { rows = rows.filter(r => !(r.col === col && r.id === id)); rows.push({ col, id, data, updated: Date.now() }); save(); },
    del: async (col, id) => { rows = rows.filter(r => !(r.col === col && r.id === id)); save(); },
    version: async () => rows.reduce((m, r) => Math.max(m, r.updated), 0) + rows.length,
  };
}

/* ---------- session par cookie signé ---------- */
const sign = v => crypto.createHmac("sha256", SECRET).update(v).digest("hex");
const cookieOf = req => Object.fromEntries((req.headers.cookie || "").split(";").map(c => c.trim().split("=").map(decodeURIComponent)).filter(p => p[0]));
function authed(req) { const c = cookieOf(req).tinado; if (!c) return false; const [v, s] = c.split("."); return s && crypto.timingSafeEqual(Buffer.from(sign(v)), Buffer.from(s.padEnd(64, "0").slice(0, 64))); }

const app = express();
app.use(express.json({ limit: "300kb" }));
app.use((req, res, next) => { res.set("X-Content-Type-Options", "nosniff"); next(); });

app.post("/api/login", (req, res) => {
  const code = String(req.body?.code || "");
  const ok = code.length === CODE.length && crypto.timingSafeEqual(Buffer.from(code), Buffer.from(CODE));
  if (!ok) return res.status(401).json({ error: "Code incorrect" });
  const v = String(Date.now());
  res.set("Set-Cookie", `tinado=${encodeURIComponent(v + "." + sign(v))}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${60 * 60 * 24 * 90}${process.env.NODE_ENV === "production" ? "; Secure" : ""}`);
  res.json({ ok: true });
});
app.post("/api/logout", (req, res) => { res.set("Set-Cookie", "tinado=; Path=/; Max-Age=0"); res.json({ ok: true }); });
app.use("/api", (req, res, next) => authed(req) ? next() : res.status(401).json({ error: "Non connecté" }));
app.get("/api/version", async (req, res) => res.json({ v: await store.version() }));
app.get("/api/all", async (req, res) => {
  const out = { reservations: [], contacts: [], commandes: [], activite: [] };
  for (const r of await store.all()) if (out[r.col]) out[r.col].push({ id: r.id, ...r.data });
  out.activite.sort((a, b) => b.le - a.le); out.activite = out.activite.slice(0, 300);
  res.json({ data: out, v: await store.version() });
});
const valid = (col, id) => COLS.has(col) && /^[A-Za-z0-9_-]{1,64}$/.test(id);
app.put("/api/:col/:id", async (req, res) => {
  const { col, id } = req.params; if (!valid(col, id) || typeof req.body !== "object" || Array.isArray(req.body)) return res.status(400).json({ error: "Requête invalide" });
  await store.put(col, id, req.body); res.json({ ok: true });
});
app.delete("/api/:col/:id", async (req, res) => {
  const { col, id } = req.params; if (!valid(col, id)) return res.status(400).json({ error: "Requête invalide" });
  await store.del(col, id); res.json({ ok: true });
});
app.use(express.static(path.join(__dirname, "public"), { extensions: ["html"] }));

store.init().then(() => app.listen(PORT, () => console.log("CRM Maison Tinado sur le port " + PORT))).catch(e => { console.error(e); process.exit(1); });
