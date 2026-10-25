// OURS (P4). Recall Storm viewer. Static, no network beyond this local server.
// Data: viewer/data/live/* (python3 viewer/build_data.py) with per-view fallback to viewer/data/fixture/*.
import * as THREE from "three";
import { OrbitControls } from "./OrbitControls.js";

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fmt = (n) => (n == null || isNaN(n) ? "–" : Math.round(n).toLocaleString("en-US"));
const fmtK = (n) => (n >= 1e6 ? (n / 1e6).toFixed(2) + "M" : n >= 1e3 ? (n / 1e3).toFixed(n >= 1e5 ? 0 : 1) + "K" : String(Math.round(n)));
const BUCKETS = [[0, 200e3, "0–200K"], [200e3, 400e3, "200K–400K"], [400e3, 600e3, "400K–600K"], [600e3, Infinity, "600K+"]];
const COL = { grey: "#5b6474", amber: "#f5a623", green: "#3ddc84", red: "#ff4d5e", blue: "#4da3ff", teal: "#2ec4b6", violet: "#b48cff" };
const DEADLINE_DEFAULT = "2027-01-01T00:00:00-08:00";

async function getJSON(url) {
  const r = await fetch(url + (url.includes("?") ? "&" : "?") + "v=" + Date.now(), { cache: "no-store" });
  if (!r.ok) throw new Error(url + " " + r.status);
  return r.json();
}

// ------------------------------------------------------------------ data sources (live first, fixture fallback)
const S = { live: null, fix: null, cache: new Map() };
async function loadIndexes() {
  try { S.live = await getJSON("data/live/index.json"); } catch { S.live = null; }
  try { S.fix = await getJSON("data/fixture/index.json"); } catch { S.fix = null; }
  const b = $("built");
  b.innerHTML = S.live ? `live data built <b>${esc(S.live.built_at)}</b>` : `<span class="badge fixture">NO LIVE DATA</span> run <code>python3 viewer/build_data.py</code>`;
}
// options for a kind: live names first; fixture names only when that kind has no live entry
function options(kind) {
  const live = (S.live?.[kind] || []).map((n) => ({ key: "live:" + n, name: n, fixture: false }));
  const fix = (S.fix?.[kind] || []).map((n) => ({ key: "fixture:" + n, name: n + " (FIXTURE)", fixture: true }));
  return live.length ? live : fix;
}
async function loadKey(prefix, key) {
  const [where, name] = key.split(/:(.*)/s);
  const file = `${prefix}_${name}.json`;
  const ck = prefix + key + "@" + (where === "live" ? S.live?.files?.[file] ?? S.live?.sig : "fixture");
  if (S.cache.has(ck)) return S.cache.get(ck);
  const d = await getJSON(`data/${where}/${file}`);
  d.__fixture = where === "fixture" || !!d.fixture;
  d.__where = where;
  for (const k of S.cache.keys()) if (k.startsWith(prefix + key + "@")) S.cache.delete(k);   // drop stale versions
  S.cache.set(ck, d);
  return d;
}
function fillSelect(sel, opts, keep, fallback) {
  const prev = keep ?? sel.value;
  sel.innerHTML = opts.map((o) => `<option value="${esc(o.key)}">${esc(o.name)}</option>`).join("");
  if (opts.some((o) => o.key === prev)) sel.value = prev;
  else if (fallback && opts.some((o) => o.key === fallback)) sel.value = fallback;
  sel.style.display = opts.length ? "" : "none";
}
function setBadges(viewId, fixture, extra = "") {
  const el = document.querySelector(`#${viewId} .vhead .badges`);
  if (el) el.innerHTML = (fixture ? `<span class="badge fixture">FIXTURE — fake data</span>` : `<span class="badge real">REAL ARTIFACT</span>`) + extra;
}

// ------------------------------------------------------------------ tooltip
const tip = $("tip");
function showTip(e, html) { tip.innerHTML = html; tip.style.display = "block"; tip.style.left = Math.min(innerWidth - 540, e.clientX + 14) + "px"; tip.style.top = e.clientY + 14 + "px"; }
function hideTip() { tip.style.display = "none"; }

// ------------------------------------------------------------------ tabs
const VIEWS = ["map", "store", "hops", "code", "fail"];
let currentView = "map";
function show(v) {
  currentView = v;
  for (const b of document.querySelectorAll("#tabs button")) b.classList.toggle("on", b.dataset.v === v);
  for (const id of VIEWS) $("v-" + id).classList.toggle("on", id === v);
  $("transportwrap").style.display = v === "map" || v === "store" ? "" : "none";
  if (v === "store") store3d.resize();
  if (v === "hops") drawHops();
  if (v === "code") drawWall();
  try { localStorage.setItem("rs_view", v); } catch {}
}
document.querySelectorAll("#tabs button").forEach((b) => (b.onclick = () => show(b.dataset.v)));
addEventListener("keydown", (e) => {
  if (e.target.matches("input, select, textarea")) return;
  const i = "12345".indexOf(e.key);
  if (i >= 0) show(VIEWS[i]);
  if (e.key === " " && (currentView === "map" || currentView === "store")) { e.preventDefault(); togglePlay(); }
});

// ------------------------------------------------------------------ drill model + replay clock
const D = { data: null, evT: [], tMin: 0, tMax: 1, tz: -8 * 60, taskById: new Map(), tasksByStore: new Map(), storeById: new Map(),
  verdictBySku: new Map(), evidenceById: new Map(), rulesById: new Map(), deadline: Date.parse(DEADLINE_DEFAULT) };
const R = { t: 0, playing: false, last: 0, cursor: 0, st: null };

function parseLoc(loc) {
  if (loc && typeof loc === "object") return { aisle: String(loc.aisle ?? "?"), bay: +loc.bay || 1, shelf: +loc.shelf || 1, pos: +loc.pos || 1 };
  const m = String(loc ?? "").match(/([A-Za-z]*\d+)\D+(\d+)\D+(\d+)\D+(\d+)/);
  return m ? { aisle: m[1], bay: +m[2], shelf: +m[3], pos: +m[4] } : null;
}
const locKey = (l) => (l ? `${l.aisle}|${l.bay}|${l.shelf}|${l.pos}` : "");
const parseT = (t) => (typeof t === "number" ? t * 1000 : Date.parse(t));

function setDrill(d) {
  D.data = d;
  const ev = d.events || [];
  D.evT = ev.map((e) => parseT(e.t));
  ev.forEach((e, i) => { e._t = D.evT[i]; e._loc = parseLoc(e.loc); });
  const finite = D.evT.filter((x) => isFinite(x));
  D.tMin = finite.length ? finite.reduce((a, b) => Math.min(a, b)) : 0;
  D.tMax = finite.length ? finite.reduce((a, b) => Math.max(a, b)) : 1;
  if (D.tMax <= D.tMin) D.tMax = D.tMin + 60e3;
  const m = String(ev[0]?.t ?? "").match(/([+-])(\d\d):?(\d\d)$/);
  D.tz = m ? (m[1] === "-" ? -1 : 1) * (+m[2] * 60 + +m[3]) : -8 * 60;
  D.taskById = new Map(); D.tasksByStore = new Map();
  for (const t of d.plan?.shelf_task || []) {
    t._loc = parseLoc(t.loc); t._ev = {};
    D.taskById.set(t.task_id, t);
    if (!D.tasksByStore.has(t.store_id)) D.tasksByStore.set(t.store_id, []);
    D.tasksByStore.get(t.store_id).push(t);
  }
  for (const e of ev) {               // tasks known only from events (no plan.jsonl yet)
    let t = D.taskById.get(e.task_id);
    if (!t && e.task_id != null) {
      t = { task_id: e.task_id, store_id: e.store_id, sku_id: null, action: "PULL", _loc: e._loc, _ev: {}, _implicit: true };
      D.taskById.set(e.task_id, t);
      if (!D.tasksByStore.has(e.store_id)) D.tasksByStore.set(e.store_id, []);
      D.tasksByStore.get(e.store_id).push(t);
    }
    if (t && t._ev[e.kind] == null) t._ev[e.kind] = e._t;
  }
  D.storeById = new Map((d.stores || []).map((s) => [s.store_id, s]));
  for (const sid of D.tasksByStore.keys()) if (!D.storeById.has(sid)) D.storeById.set(sid, { store_id: sid });
  D.verdictBySku = new Map((d.plan?.sku_verdict || []).map((v) => [v.sku_id, v]));
  D.evidenceById = new Map((d.plan?.evidence || []).map((v) => [v.evidence_id, v]));
  D.rulesById = new Map((d.rules || []).map((r) => [r.rule_id, r]));
  const pb = (d.plan?.store_playbook || []).find((p) => p.deadline);
  D.deadline = Date.parse(pb?.deadline || DEADLINE_DEFAULT);
  R.t = D.tMin; resetReplay();
}

function resetReplay() {
  R.cursor = 0;
  R.st = { skus: new Set(), pulls: 0, done: 0, perStore: new Map() };
  for (const sid of D.storeById.keys()) R.st.perStore.set(sid, { started: false, done: 0, total: (D.tasksByStore.get(sid) || []).length });
}
function advanceTo(t) {
  if (t < R.lastApplied) resetReplay();
  const ev = D.data?.events || [];
  while (R.cursor < ev.length && !(D.evT[R.cursor] > t)) {
    const e = ev[R.cursor++];
    const ps = R.st.perStore.get(e.store_id);
    if (ps) ps.started = true;
    if (e.kind === "PULL") {
      R.st.pulls++;
      const task = D.taskById.get(e.task_id);
      if (task?.sku_id) R.st.skus.add(task.sku_id);
    } else if (e.kind === "DONE") { R.st.done++; if (ps) ps.done++; }
  }
  R.lastApplied = t;
}
R.lastApplied = -Infinity;

function localClock(ms) {
  const d = new Date(ms + D.tz * 60e3);
  const mo = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][d.getUTCMonth()];
  const hh = String(d.getUTCHours()).padStart(2, "0"), mm = String(d.getUTCMinutes()).padStart(2, "0"), ss = String(d.getUTCSeconds()).padStart(2, "0");
  return `${mo} ${d.getUTCDate()} ${hh}:${mm}:${ss}`;
}
function speedSimPerSec() {           // simulated ms per real ms
  const v = $("speed").value;
  return v === "real60" ? 60 : (D.tMax - D.tMin) / (+v * 1000);
}
function togglePlay() {
  if (!D.data) return;
  if (!R.playing && R.t >= D.tMax) R.t = D.tMin;
  R.playing = !R.playing; R.last = performance.now();
  $("play").textContent = R.playing ? "❚❚ Pause" : "▶ Play";
}
$("play").onclick = togglePlay;
$("restart").onclick = () => { R.t = D.tMin; resetReplay(); R.lastApplied = -Infinity; };
$("scrub").oninput = (e) => { R.t = D.tMin + (D.tMax - D.tMin) * (+e.target.value / 1000); };

function tick(now) {
  if (R.playing && D.data) {
    const dt = now - R.last; R.last = now;
    R.t = Math.min(D.tMax, R.t + dt * speedSimPerSec());
    if (R.t >= D.tMax) { R.playing = false; $("play").textContent = "▶ Play"; }
  }
  if (D.data) {
    advanceTo(R.t);
    $("scrub").value = String(Math.round(((R.t - D.tMin) / (D.tMax - D.tMin)) * 1000));
    const tzs = (D.tz < 0 ? "−" : "+") + String(Math.abs(D.tz / 60)).padStart(2, "0") + ":00";
    $("clock").innerHTML = `${localClock(R.t)} <small>simulated store-local time (UTC${tzs}) · ${fmt(R.cursor)} / ${fmt(D.evT.length)} events</small>`;
    if (currentView === "map") updateMap();
    if (currentView === "store") store3d.update(now);
  }
  requestAnimationFrame(tick);
}

// ------------------------------------------------------------------ California map
// Coarse California outline (lon, lat), hand-simplified; good enough for a projector.
const CA = [[-124.21, 41.99], [-120.0, 41.99], [-120.0, 39.0], [-114.63, 35.0], [-114.63, 34.87], [-114.43, 34.3], [-114.13, 34.27],
  [-114.43, 34.08], [-114.53, 33.93], [-114.5, 33.69], [-114.73, 33.4], [-114.69, 33.08], [-114.47, 32.94], [-114.72, 32.72],
  [-117.12, 32.53], [-117.25, 32.68], [-117.28, 33.0], [-117.6, 33.39], [-118.08, 33.72], [-118.29, 33.71], [-118.41, 33.75],
  [-118.39, 33.9], [-118.52, 34.03], [-118.8, 34.0], [-119.21, 34.14], [-119.6, 34.42], [-120.47, 34.45], [-120.64, 34.57],
  [-120.61, 34.9], [-120.64, 35.14], [-120.86, 35.36], [-121.29, 35.66], [-121.89, 36.31], [-121.94, 36.58], [-121.79, 36.8],
  [-122.0, 36.96], [-122.4, 37.19], [-122.51, 37.52], [-122.51, 37.78], [-122.98, 38.0], [-123.03, 38.3], [-123.72, 38.92],
  [-123.83, 39.36], [-123.85, 39.8], [-124.11, 40.1], [-124.41, 40.44], [-124.11, 40.85], [-124.08, 41.46], [-124.21, 41.99]];
const MAP = { W: 900, H: 1000, dots: new Map(), proj: null };
function buildMap() {
  const svg = $("map");
  const k = Math.cos((37.2 * Math.PI) / 180);
  const xs = CA.map((p) => p[0] * k), ys = CA.map((p) => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const pad = 30, W = MAP.W, H = MAP.H;
  const sc = Math.min((W - 2 * pad) / (x1 - x0), (H - 2 * pad) / (y1 - y0));
  const ox = (W - sc * (x1 - x0)) / 2, oy = (H - sc * (y1 - y0)) / 2;
  MAP.proj = (lon, lat) => [ox + (lon * k - x0) * sc, oy + (y1 - lat) * sc];
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const poly = CA.map((p) => MAP.proj(p[0], p[1]).map((v) => v.toFixed(1)).join(",")).join(" ");
  let html = `<polygon class="ca" points="${poly}"/>`;
  html += `<text x="${W - 40}" y="${H - 20}" text-anchor="end" fill="#3a4a63" font-size="22">CALIFORNIA (outline simplified)</text>`;
  const stores = [...D.storeById.values()];
  const noGeo = stores.filter((s) => s.lat == null || s.lon == null);
  const big = stores.length < 60;
  stores.forEach((s, i) => {
    let [x, y] = s.lat != null && s.lon != null ? MAP.proj(s.lon, s.lat) : [40 + (noGeo.indexOf(s) % 10) * 22, H - 60 - Math.floor(noGeo.indexOf(s) / 10) * 22];
    // nudge co-located stores apart so every dot stays clickable
    const r = s.format === "SUPERCENTER" || s.format === "SAMS" ? (big ? 13 : 7) : (big ? 10 : 5);
    html += `<circle class="store" data-id="${esc(s.store_id)}" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r}" fill="${COL.grey}"/>`;
    if (big) html += `<text class="city" x="${(x + r + 4).toFixed(1)}" y="${(y + 4).toFixed(1)}">${esc(s.city || s.store_id)}</text>`;
  });
  svg.innerHTML = html;
  // spread exact duplicates
  const seen = new Map();
  for (const c of svg.querySelectorAll("circle.store")) {
    const key = c.getAttribute("cx") + "," + c.getAttribute("cy");
    const n = seen.get(key) || 0; seen.set(key, n + 1);
    if (n) { const a = n * 2.4, d = 9 + 3 * n; c.setAttribute("cx", (+c.getAttribute("cx") + Math.cos(a) * d).toFixed(1)); c.setAttribute("cy", (+c.getAttribute("cy") + Math.sin(a) * d).toFixed(1)); }
    MAP.dots.set(c.dataset.id, c);
  }
  MAP.dots = new Map([...svg.querySelectorAll("circle.store")].map((c) => [c.dataset.id, c]));
  svg.onmousemove = (e) => {
    const c = e.target.closest("circle.store");
    if (!c) return hideTip();
    const s = D.storeById.get(c.dataset.id), ps = R.st.perStore.get(c.dataset.id);
    showTip(e, `<b>${esc(s.store_id)}</b> ${esc(s.city || "")} · ${esc(s.format || "")}\n${esc(s.dc_id || "")} ${esc(s.district || "")}\ntasks done ${ps?.done ?? 0} / ${ps?.total ?? 0}`);
  };
  svg.onmouseleave = hideTip;
  svg.onclick = (e) => { const c = e.target.closest("circle.store"); if (c) { openStore(c.dataset.id); show("store"); } };
  // store list
  $("storelist").innerHTML = stores.map((s) => `<div class="row" data-id="${esc(s.store_id)}"><span>${esc(s.store_id)}</span>
    <div class="bar"><div style="width:0%"></div></div><span class="pct">0/0</span></div>`).join("");
  $("storelist").onclick = (e) => { const r = e.target.closest(".row"); if (r) { openStore(r.dataset.id); show("store"); } };
}
function lerpColor(a, b, f) {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16)), pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  return "#" + pa.map((v, i) => Math.round(v + (pb[i] - v) * f).toString(16).padStart(2, "0")).join("");
}
let mapRows = null;
function updateMap() {
  if (!R.st) return;
  let complete = 0, totalTasks = 0;
  if (!mapRows) mapRows = new Map([...$("storelist").querySelectorAll(".row")].map((r) => [r.dataset.id, r]));
  for (const [sid, ps] of R.st.perStore) {
    totalTasks += ps.total;
    const isDone = ps.total > 0 && ps.done >= ps.total;
    if (isDone) complete++;
    const col = !ps.started ? COL.grey : isDone ? COL.green : lerpColor(COL.amber, "#b8d65a", ps.total ? ps.done / ps.total : 0);
    const c = MAP.dots.get(sid);
    if (c && c.getAttribute("fill") !== col) c.setAttribute("fill", col);
    const row = mapRows.get(sid);
    if (row) {
      const pct = ps.total ? (100 * ps.done) / ps.total : 0;
      const bar = row.querySelector(".bar > div");
      bar.style.width = pct.toFixed(1) + "%"; bar.style.background = isDone ? COL.green : COL.amber;
      row.querySelector(".pct").textContent = `${ps.done}/${ps.total}`;
    }
  }
  $("c-skus").textContent = fmt(R.st.skus.size);
  $("c-pulls").textContent = fmt(R.st.pulls);
  $("c-tasks").textContent = `${fmt(R.st.done)}`;
  $("c-tasks").nextElementSibling.textContent = `tasks done of ${fmt(totalTasks)}`;
  $("c-stores").textContent = `${complete}`;
  $("c-stores").nextElementSibling.textContent = `stores complete of ${R.st.perStore.size}`;
  const left = D.deadline - R.t;
  const h = Math.floor(Math.abs(left) / 3600e3), m = Math.floor((Math.abs(left) % 3600e3) / 60e3);
  $("deadline").innerHTML = left > 0 ? `Deadline 2027-01-01 00:00 local: <b class="good">${h} h ${m} min</b> to spare at this point`
    : `<b class="bad">PAST THE DEADLINE by ${h} h ${m} min</b>`;
}

// ------------------------------------------------------------------ 3D store
const store3d = (() => {
  const el = $("store3d");
  let renderer, scene, camera, controls, inited = false;
  let facMesh = null, facList = [], hotIdx = [], assocObjs = [], sid = null, group = null;
  const tmpM = new THREE.Matrix4(), tmpC = new THREE.Color();
  const AISLE_GAP = 4.2, BAY_LEN = 1.6, SHELF_H = 0.42, DEPTH = 0.8;
  const geo = { aisleX: new Map(), maxBay: 1, posPerBay: 6 };

  function init() {
    if (inited) return; inited = true;
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(2, devicePixelRatio));
    el.appendChild(renderer.domElement);
    scene = new THREE.Scene(); scene.background = new THREE.Color("#070a0f");
    camera = new THREE.PerspectiveCamera(45, 1, 0.1, 500);
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; controls.maxPolarAngle = Math.PI * 0.49;
    scene.add(new THREE.HemisphereLight(0xcfe3ff, 0x202530, 1.1));
    const dl = new THREE.DirectionalLight(0xffffff, 1.2); dl.position.set(10, 20, 8); scene.add(dl);
    const ray = new THREE.Raycaster(), mouse = new THREE.Vector2();
    renderer.domElement.addEventListener("click", (e) => {
      if (!facMesh) return;
      const r = renderer.domElement.getBoundingClientRect();
      mouse.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
      ray.setFromCamera(mouse, camera);
      const hit = ray.intersectObject(facMesh)[0];
      if (hit && hit.instanceId != null) { const f = facList[hit.instanceId]; showCardsFor(f.sku_id, f); }
    });
    renderer.domElement.addEventListener("mousemove", (e) => {
      if (!facMesh) return;
      const r = renderer.domElement.getBoundingClientRect();
      mouse.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
      ray.setFromCamera(mouse, camera);
      const hit = ray.intersectObject(facMesh)[0];
      if (hit && hit.instanceId != null) {
        const f = facList[hit.instanceId], sku = D.data.skus?.[f.sku_id], v = D.verdictBySku.get(f.sku_id);
        showTip(e, `<b>${esc(sku?.name || f.sku_id)}</b>\n${esc(f.sku_id)} · ${esc(f.loc.aisle)} bay ${f.loc.bay} shelf ${f.loc.shelf} pos ${f.loc.pos}${v ? "\nverdict " + esc(v.verdict) : ""}${f._tasks.length ? "\ntasks: " + f._tasks.map((t) => t.action).join(", ") : ""}`);
      } else hideTip();
    });
    renderer.domElement.addEventListener("mouseleave", hideTip);
    resize();
  }
  function resize() {
    if (!inited) return;
    const w = el.clientWidth, h = el.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  addEventListener("resize", resize);
  const hash = (s) => { let h = 2166136261; for (const c of String(s)) h = Math.imul(h ^ c.charCodeAt(0), 16777619); return h >>> 0; };
  function facPos(l) {
    const ax = geo.aisleX.get(l.aisle) ?? 0;
    const side = 0; // single-sided gondolas, product faces +x (the walkway)
    const z = (l.bay - 1) * BAY_LEN + ((l.pos - 0.5) / geo.posPerBay) * BAY_LEN;
    const y = 0.25 + (l.shelf - 1) * SHELF_H + 0.14;
    return new THREE.Vector3(ax + side, y, z);
  }
  const walkPos = (l) => {
    if (!l) return new THREE.Vector3(-2.5, 0, -2.5);
    const ax = geo.aisleX.get(l.aisle) ?? 0;
    return new THREE.Vector3(ax + 1.3, 0, (l.bay - 1) * BAY_LEN + ((l.pos - 0.5) / geo.posPerBay) * BAY_LEN);
  };

  function load(storeId) {
    init();
    sid = storeId;
    if (group) { scene.remove(group); group.traverse((o) => { o.geometry?.dispose?.(); o.material?.dispose?.(); }); }
    group = new THREE.Group(); scene.add(group);
    facList = (D.data.facings || []).filter((f) => f.store_id === storeId).map((f) => ({ ...f, loc: parseLoc(f.loc), _tasks: [] }));
    const tasks = D.tasksByStore.get(storeId) || [];
    const byLoc = new Map(facList.map((f) => [locKey(f.loc), f]));
    for (const t of tasks) {               // a task at a location with no facing record still shows up
      let f = byLoc.get(locKey(t._loc));
      if (!f && t._loc) { f = { store_id: storeId, sku_id: t.sku_id, loc: t._loc, units: t.qty_units, _tasks: [] }; facList.push(f); byLoc.set(locKey(t._loc), f); }
      if (f) f._tasks.push(t);
    }
    const aisles = [...new Set(facList.map((f) => f.loc.aisle))].sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
    geo.aisleX = new Map(aisles.map((a, i) => [a, i * AISLE_GAP]));
    geo.maxBay = Math.max(1, ...facList.map((f) => f.loc.bay));
    geo.posPerBay = Math.max(6, ...facList.map((f) => f.loc.pos));
    const maxShelf = Math.max(5, ...facList.map((f) => f.loc.shelf));
    const len = geo.maxBay * BAY_LEN, width = Math.max(1, aisles.length) * AISLE_GAP;
    // floor + walkway paint
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(width + 8, len + 8), new THREE.MeshStandardMaterial({ color: "#1a2029" }));
    floor.rotation.x = -Math.PI / 2; floor.position.set(width / 2 - 2, 0, len / 2 - 1.5); group.add(floor);
    const grid = new THREE.GridHelper(Math.max(width, len) + 8, Math.round(Math.max(width, len) + 8), 0x2a3344, 0x1f2633);
    grid.position.set(width / 2 - 2, 0.01, len / 2 - 1.5); group.add(grid);
    // gondolas: back panel + shelf boards per aisle
    const gMat = new THREE.MeshStandardMaterial({ color: "#3b4658" }), sMat = new THREE.MeshStandardMaterial({ color: "#566278" });
    for (const a of aisles) {
      const x = geo.aisleX.get(a);
      const back = new THREE.Mesh(new THREE.BoxGeometry(0.08, maxShelf * SHELF_H + 0.4, len), gMat);
      back.position.set(x - DEPTH / 2, (maxShelf * SHELF_H + 0.4) / 2, len / 2); group.add(back);
      for (let s = 0; s < maxShelf; s++) {
        const b = new THREE.Mesh(new THREE.BoxGeometry(DEPTH, 0.04, len), sMat);
        b.position.set(x, 0.25 + s * SHELF_H, len / 2); group.add(b);
      }
      group.add(label(a, new THREE.Vector3(x, maxShelf * SHELF_H + 0.9, -0.6)));
    }
    // facings as instanced boxes
    const box = new THREE.BoxGeometry(DEPTH * 0.8, 0.26, (BAY_LEN / geo.posPerBay) * 0.85);
    facMesh = new THREE.InstancedMesh(box, new THREE.MeshStandardMaterial({ roughness: 0.6 }), Math.max(1, facList.length));
    hotIdx = [];
    facList.forEach((f, i) => {
      const p = facPos(f.loc);
      tmpM.makeTranslation(p.x, p.y, p.z); facMesh.setMatrixAt(i, tmpM);
      f._base = new THREE.Color().setHSL((hash(f.sku_id) % 360) / 360, 0.25, 0.32);
      facMesh.setColorAt(i, f._base);
      if (f._tasks.length) hotIdx.push(i);
    });
    facMesh.count = facList.length;
    facMesh.instanceMatrix.needsUpdate = true; if (facMesh.instanceColor) facMesh.instanceColor.needsUpdate = true;
    group.add(facMesh);
    // associates
    assocObjs = [];
    const evs = (D.data.events || []).filter((e) => e.store_id === storeId);
    const byA = new Map();
    for (const e of evs) { if (!byA.has(e.associate_id)) byA.set(e.associate_id, []); byA.get(e.associate_id).push(e); }
    let k = 0;
    for (const [aid, list] of byA) {
      const hue = (k++ * 0.137) % 1;
      const col = new THREE.Color().setHSL(hue, 0.8, 0.6);
      const g = new THREE.Group();
      const body = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 1.1, 14), new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: 0.35 }));
      body.position.y = 0.55;
      const head = new THREE.Mesh(new THREE.SphereGeometry(0.2, 14, 10), new THREE.MeshStandardMaterial({ color: "#f1d3b3" }));
      head.position.y = 1.32;
      g.add(body, head, label(aid.replace(storeId + "-", ""), new THREE.Vector3(0, 1.9, 0), 0.6));
      group.add(g);
      assocObjs.push({ aid, list, g });
    }
    // entrance marker
    const door = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.05, 0.6), new THREE.MeshStandardMaterial({ color: COL.blue, emissive: COL.blue, emissiveIntensity: 0.4 }));
    door.position.set(-2.5, 0.03, -2.5); group.add(door); group.add(label("ENTRANCE", new THREE.Vector3(-2.5, 0.8, -2.5), 0.8));
    const cx = width / 2 - 2, cz = len / 2;
    camera.position.set(cx - width * 0.4 - 6, Math.max(9, len * 0.55), -len * 0.35 - 6);
    controls.target.set(cx, 0.8, cz); controls.update();
    resize();
    const s = D.storeById.get(storeId) || {};
    $("store3dinfo").innerHTML = `<b style="color:#fff;font-size:20px">${esc(storeId)}</b> ${esc(s.city || "")} · ${esc(s.format || "")} · ${aisles.length} aisles · ${facList.length} facings · ${tasks.length} tasks · ${byA.size} associates<br>
      <span style="color:${COL.red}">■</span> pull pending (flashing) <span style="color:${COL.amber}">■</span> hold &amp; verify <span style="color:${COL.green}">■</span> substitute placed <span style="color:#666">■</span> pulled/empty · drag to orbit, click a product`;
  }
  function label(text, pos, scale = 1) {
    const c = document.createElement("canvas"); c.width = 256; c.height = 64;
    const x = c.getContext("2d"); x.font = "bold 40px system-ui"; x.fillStyle = "#e8edf5"; x.textAlign = "center"; x.textBaseline = "middle"; x.fillText(text, 128, 32);
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), depthTest: false, transparent: true }));
    sp.scale.set(2 * scale, 0.5 * scale, 1); sp.position.copy(pos); return sp;
  }
  function pathPoints(a, b) {
    if (a.x === b.x || Math.abs(a.x - b.x) < 0.01) return [a, b];
    const front = -1.5; // cross-aisle at the front of the store
    return [a, new THREE.Vector3(a.x, 0, front), new THREE.Vector3(b.x, 0, front), b];
  }
  function along(pts, f) {
    const segs = []; let L = 0;
    for (let i = 1; i < pts.length; i++) { const d = pts[i].distanceTo(pts[i - 1]); segs.push(d); L += d; }
    let want = L * Math.min(1, Math.max(0, f));
    for (let i = 0; i < segs.length; i++) { if (want <= segs[i] || i === segs.length - 1) return pts[i].clone().lerp(pts[i + 1], segs[i] ? want / segs[i] : 1); want -= segs[i]; }
    return pts[pts.length - 1].clone();
  }
  function update(now) {
    if (!inited || !sid) return;
    const t = R.t, flash = 0.5 + 0.5 * Math.sin(now / 140);
    for (const i of hotIdx) {
      const f = facList[i];
      let pending = null, placed = false, pulled = false, held = false;
      for (const task of f._tasks) {
        const done = task._ev.DONE != null && task._ev.DONE <= t;
        if (task.action === "PLACE_SUB") { if (done || (task._ev.PLACE != null && task._ev.PLACE <= t)) placed = true; else pending = pending || "SUB"; }
        else if (task.action === "HOLD_VERIFY") { if (done) held = true; else pending = "HOLD"; }
        else { if (done || (task._ev.PULL != null && task._ev.PULL <= t)) pulled = true; else pending = "PULL"; }
      }
      if (pending === "PULL" || (pending === "SUB" && !pulled)) tmpC.set(COL.red).lerp(new THREE.Color("#300"), 1 - flash);
      else if (pending === "HOLD") tmpC.set(COL.amber).lerp(new THREE.Color("#320"), 1 - flash);
      else if (pending === "SUB") tmpC.set(COL.blue).lerp(new THREE.Color("#023"), 1 - flash);
      else if (placed) tmpC.set(COL.green);
      else if (held) tmpC.set(COL.amber);
      else if (pulled) tmpC.set("#222831");
      else tmpC.copy(f._base);
      facMesh.setColorAt(i, tmpC);
    }
    if (facMesh?.instanceColor) facMesh.instanceColor.needsUpdate = true;
    for (const a of assocObjs) {
      const L = a.list; let i = -1, lo = 0, hi = L.length - 1;
      while (lo <= hi) { const m = (lo + hi) >> 1; if (L[m]._t <= t) { i = m; lo = m + 1; } else hi = m - 1; }
      let p;
      if (i < 0) p = walkPos(null);
      else {
        const e = L[i], prev = i > 0 ? L[i - 1]._loc : null, nxt = L[i + 1];
        if (e.kind === "MOVE" && nxt && nxt._t > e._t) p = along(pathPoints(walkPos(prev), walkPos(e._loc)), (t - e._t) / (nxt._t - e._t));
        else p = walkPos(e._loc);
      }
      a.g.position.lerp(p, R.playing ? 0.5 : 1);
    }
    controls.update();
    renderer.render(scene, camera);
  }
  return { load, update, resize, get sid() { return sid; } };
})();

// ------------------------------------------------------------------ evidence cards
const DECOY_RE = /(red\s*(no\.?\s*)?40|d&c\s*red\s*(no\.?\s*)?33|\b\d+\s+red\s+apples?|red\s*40\s*lake)/gi;
const DECOY_TEST = new RegExp(DECOY_RE.source, "i");
function hiIngredients(ing, v) {
  ing = String(ing || "");
  const m = v?.match;
  let s = null, e = null, text = null;
  if (m && typeof m === "object") { s = m.start; e = m.end; text = m.text; }
  else if (typeof m === "string") text = m;
  if ((s == null || e == null || ing.slice(s, e).toLowerCase() !== String(text ?? ing.slice(s, e)).toLowerCase()) && text) {
    const i = ing.toLowerCase().indexOf(String(text).toLowerCase());
    if (i >= 0) { s = i; e = i + String(text).length; }
  }
  const cls = v?.verdict === "HOLD_VERIFY" ? "hold" : "";
  let out;
  if (s != null && e != null && e > s && e <= ing.length) out = esc(ing.slice(0, s)) + `<mark class="${cls}">${esc(ing.slice(s, e))}</mark>` + esc(ing.slice(e));
  else out = esc(ing);
  if (v?.verdict === "KEEP") out = out.replace(DECOY_RE, (x) => `<mark class="decoy" title="decoy: not Red No. 3">${x}</mark>`);
  return out;
}
function clauseHtml(ev) {
  const rule = D.rulesById.get(ev?.rule_id);
  const sp = ev?.source_span;
  if (rule?.source_text && Array.isArray(sp) && sp.length === 2 && sp[1] > sp[0]) {
    const t = rule.source_text, a = Math.max(0, sp[0] - 90), b = Math.min(t.length, sp[1] + 40);
    return `${a > 0 ? "…" : ""}${esc(t.slice(a, sp[0]))}<mark class="span">${esc(t.slice(sp[0], sp[1]))}</mark>${esc(t.slice(sp[1], b))}${b < t.length ? "…" : ""}`;
  }
  return esc(typeof sp === "string" ? sp : rule?.source_text?.slice(0, 200) || "");
}
function cardHtml(skuId, why = "") {
  const v = D.verdictBySku.get(skuId), sku = D.data.skus?.[skuId] || {};
  const ev = v ? D.evidenceById.get(v.evidence_id) : null;
  const verdict = v?.verdict || "?";
  return `<div class="card ${esc(verdict)}">
    ${why ? `<div class="note" style="font-size:13px;text-transform:uppercase;letter-spacing:.5px">${esc(why)}</div>` : ""}
    <h4>${esc(sku.name || skuId)} <span class="v ${esc(verdict)}">${esc(verdict)}</span></h4>
    <div class="meta">${esc(skuId)} · GTIN ${esc(v?.gtin || "")} · ${esc(sku.brand || "")} · ${esc(sku.category || "")} · decided by ${esc(v?.decided_by || "?")}</div>
    <div class="ing">${hiIngredients(sku.ingredients, v)}</div>
    <div class="why">${esc(ev?.rationale || (v ? "" : "no sku_verdict record for this SKU"))}</div>
    ${ev ? `<div class="clause"><b>${esc(ev.rule_id)}</b> · ${esc(ev.clause_ref || "")}<br>${clauseHtml(ev)}</div>` : ""}
    <div class="meta" style="margin-top:4px">src: ${esc(v?.src || "")}${ev ? " · " + esc(ev.evidence_id) + " · " + esc(ev.src || "") : ""}</div></div>`;
}
function pickTrio() {
  const vs = D.data?.plan?.sku_verdict || [];
  const ing = (v) => String(D.data.skus?.[v.sku_id]?.ingredients || "").toLowerCase();
  const inStore = new Set((D.tasksByStore.get(store3d.sid) || []).map((t) => t.sku_id));
  const pref = (arr) => arr.sort((a, b) => (inStore.has(b.sku_id) ? 1 : 0) - (inStore.has(a.sku_id) ? 1 : 0));
  const pull = pref(vs.filter((v) => v.verdict === "PULL" && /erythros/i.test(v.match?.text || ing(v))))[0] || vs.find((v) => v.verdict === "PULL");
  const hold = pref(vs.filter((v) => v.verdict === "HOLD_VERIFY" && /artificial colou?r/.test(ing(v))))[0] || vs.find((v) => v.verdict === "HOLD_VERIFY");
  const keep = pref(vs.filter((v) => v.verdict === "KEEP" && /red\s*(no\.?\s*)?40/.test(ing(v)) && !/red\s*(no\.?\s*|dye\s*)?3\b|erythros|e\s?127/.test(ing(v))))[0]
    || vs.find((v) => v.verdict === "KEEP" && DECOY_TEST.test(ing(v))) || vs.find((v) => v.verdict === "KEEP");
  return [[pull, "erythrosine caught"], [hold, "“artificial color” held"], [keep, "Red 40 decoy kept"]].filter((x) => x[0]);
}
function showTrio() {
  if (!D.data) return;
  const trio = pickTrio();
  $("cards").innerHTML = (trio.length ? trio.map(([v, why]) => cardHtml(v.sku_id, why)).join("") : `<div class="empty">No sku_verdict records in this drill yet</div>`) + taskListHtml();
}
function showCardsFor(skuId, fac) {
  const tasks = fac?._tasks || [];
  $("cards").innerHTML = cardHtml(skuId, fac ? `${fac.loc.aisle} bay ${fac.loc.bay} shelf ${fac.loc.shelf} pos ${fac.loc.pos}` : "") +
    tasks.map((t) => `<div class="card"><div class="meta">${esc(t.task_id)} · <b>${esc(t.action)}</b> · ${esc(t.associate_id || "")} · qty ${esc(t.qty_units ?? "")}${t.sub_sku_id ? " · sub " + esc(t.sub_sku_id) : ""}<br>window ${esc((t.window || []).join(" → "))}<br>src ${esc(t.src || "")}</div></div>`).join("") + taskListHtml();
}
function taskListHtml() {
  const tasks = D.tasksByStore.get(store3d.sid) || [];
  if (!tasks.length) return "";
  return `<div class="panel"><b>Tasks in ${esc(store3d.sid)}</b> (${tasks.length})<div class="tasks" id="tasklist">` +
    tasks.slice(0, 400).map((t) => `<div data-sku="${esc(t.sku_id)}">${esc(t.task_id)} ${esc(t.action)} ${esc(t.sku_id || "")} ${t._loc ? esc(t._loc.aisle + "/" + t._loc.bay + "/" + t._loc.shelf + "/" + t._loc.pos) : ""}</div>`).join("") + `</div></div>`;
}
$("cards").addEventListener("click", (e) => { const d = e.target.closest("#tasklist div"); if (d?.dataset.sku) { showCardsFor(d.dataset.sku); } });
$("trio").onclick = showTrio;
function openStore(id) {
  if (!D.data || !id) return;
  $("storesel").value = id;
  try { store3d.load(id); } catch (e) { console.error("3D store failed (WebGL?)", e); $("store3dinfo").textContent = "3D view unavailable: " + e.message; }
  showTrio();
}
$("storesel").onchange = (e) => openStore(e.target.value);

async function loadDrill() {
  const opts = options("drills");
  fillSelect($("drillsel"), opts);
  if (!opts.length) { $("mapsrc").textContent = "no drill data (live or fixture)"; return; }
  const d = await loadKey("drill", $("drillsel").value);
  if (d === D.data) return;                 // unchanged since the last load: keep the replay where it is
  const sameDrill = D.data && D.data.__key === $("drillsel").value, prevT = R.t;
  d.__key = $("drillsel").value;
  const wasPlaying = R.playing; R.playing = false;
  setDrill(d);
  if (sameDrill) R.t = Math.min(D.tMax, Math.max(D.tMin, prevT));  // re-built data: stay at the same moment
  R.lastApplied = -Infinity;
  mapRows = null; buildMap();
  const fix = d.__fixture;
  setBadges("v-map", fix, ` <span class="badge sim">SIMULATED stores, staffing, stock</span>`);
  setBadges("v-store", fix, ` <span class="badge sim">SIMULATED</span>`);
  const src = d.source || {};
  $("mapsrc").textContent = `stores: ${src.stores || "?"} · events: ${src.events || "?"} · plan: ${src.plan || "?"}`;
  $("storesrc").textContent = `facings: data/facings.jsonl · tasks: ${src.plan || "?"}`;
  const stores = [...D.storeById.values()];
  const tasksOf = (s) => (D.tasksByStore.get(s.store_id) || []).length;
  $("storesel").innerHTML = stores.map((s) => `<option value="${esc(s.store_id)}">${esc(s.store_id)} ${esc(s.city || "")} · ${esc(s.format || "")} · ${tasksOf(s)} tasks</option>`).join("");
  const prev = store3d.sid && D.storeById.has(store3d.sid) ? store3d.sid : (stores.find((s) => s.format === "SUPERCENTER" && tasksOf(s)) || stores[0])?.store_id;
  openStore(prev);
  $("play").textContent = "▶ Play";
  if (wasPlaying) togglePlay();
}
$("drillsel").onchange = loadDrill;

// ------------------------------------------------------------------ hops & seams
let RUN = null;
async function loadRun() {
  const opts = options("runs");
  // prefer the expansion run when present
  const pref = opts.find((o) => o.name.startsWith("expansion")) || opts[0];
  fillSelect($("runsel"), opts, $("runsel").value, pref?.key);
  if (!opts.length) { $("runheadline").textContent = "no run logs yet"; return; }
  RUN = await loadKey("run", $("runsel").value);
  const s = RUN.summary || {};
  setBadges("v-hops", RUN.__fixture, s.live ? ` <span class="badge live">LIVE — still generating</span>` : "");
  $("runsrc").textContent = RUN.__fixture ? "viewer/data/fixture" : (RUN.kind === "bg" ? `runs/${RUN.name}/events.jsonl` : `runs/${RUN.name}/hops.jsonl + stream_log.jsonl`);
  $("runheadline").innerHTML = `<span>${fmt(s.visible)}</span> visible tokens · <span>${fmt(s.hops)}</span> hop${s.hops === 1 ? "" : "s"} · <span>${s.minutes ?? "–"}</span> minutes · <span>$${(s.cost_usd ?? 0).toFixed(2)}</span>`;
  $("runformula").innerHTML = `cost = $10/1M × (visible ${fmt(s.visible)} + thinking ${fmt(s.thinking)}) + $2/1M × prompt tokens summed over hops (${fmt(s.prompt)})` +
    (RUN.kind === "bg" ? " · background usage: visible = total_output − total_thought" : "") + (RUN.tokens_estimated_from_bytes ? " · curve between status updates estimated from bytes" : "") +
    ` · seams: ${s.seams_pass ?? 0} PASS, ${s.seams_fail ?? 0} FAIL of ${(RUN.seams || []).length}`;
  const seams = RUN.seams || [];
  $("seams").innerHTML = seams.length ? seams.map((x) => `<div class="panel seam">
      <b>Seam ${x.n}</b> · hop ${x.hop} → ${x.hop + 1} · byte ${fmt(x.seam_byte)} · token ${fmt(x.tok)} · t = ${((x.t || 0) / 60).toFixed(1)} min
      <span class="status ${esc(x.status)}">${esc(x.status)}</span>${(x.fails || []).length ? `<div class="bad">${esc(x.fails.join("; "))}</div>` : ""}
      ${(x.notes || []).length ? `<div class="note">${esc(x.notes.join("; "))}</div>` : ""}
      <pre><span class="before">${esc(x.before)}</span><span class="cut">⟂ SEAM</span><span class="after">${esc(x.after)}</span></pre></div>`).join("")
    : `<div class="panel note">No continuation seam in this run${s.live ? " yet" : ""} (${fmt(s.hops)} hop${s.hops === 1 ? "" : "s"}). Seams appear when a hop ends with finish = CONTINUATION and a token.</div>`;
  drawHops();
}
$("runsel").onchange = loadRun;

function setupCanvas(cv) {
  const r = cv.getBoundingClientRect(), dpr = devicePixelRatio || 1;
  cv.width = Math.max(1, r.width * dpr); cv.height = Math.max(1, r.height * dpr);
  const x = cv.getContext("2d"); x.setTransform(dpr, 0, 0, dpr, 0, 0);
  return [x, r.width, r.height];
}
function drawHops() {
  const cv = $("hopchart");
  if (!RUN || currentView !== "hops") return;
  const [x, W, H] = setupCanvas(cv);
  const P = { l: 90, r: 30, t: 30, b: 50 };
  const pts = RUN.points || [];
  const tMax = Math.max(1, ...pts.map((p) => p[0])), yMax = Math.max(1000, ...pts.map((p) => p[1] + (p[2] || 0)));
  const X = (t) => P.l + (t / tMax) * (W - P.l - P.r), Y = (v) => H - P.b - (v / yMax) * (H - P.t - P.b);
  x.clearRect(0, 0, W, H);
  x.font = "15px system-ui"; x.fillStyle = "#8d98ab"; x.strokeStyle = "#2a3344"; x.lineWidth = 1;
  for (let i = 0; i <= 5; i++) {
    const v = (yMax * i) / 5; x.beginPath(); x.moveTo(P.l, Y(v)); x.lineTo(W - P.r, Y(v)); x.stroke();
    x.textAlign = "right"; x.fillText(fmtK(v), P.l - 8, Y(v) + 5);
  }
  const stepMin = tMax / 60 > 60 ? 15 : tMax / 60 > 20 ? 5 : tMax / 60 > 4 ? 1 : 0.25;
  x.textAlign = "center";
  for (let m = 0; m <= tMax / 60 + 1e-9; m += stepMin) x.fillText(m + (m ? "" : " min"), X(m * 60), H - P.b + 22);
  // hop boundaries
  for (const h of RUN.hops || []) {
    if (h.t == null) continue;
    const cont = h.finish === "CONTINUATION" || h.has_token;
    x.strokeStyle = cont ? COL.amber : "#556178"; x.setLineDash([6, 5]); x.lineWidth = 1.5;
    x.beginPath(); x.moveTo(X(h.t), P.t); x.lineTo(X(h.t), H - P.b); x.stroke(); x.setLineDash([]);
    x.fillStyle = cont ? COL.amber : "#8d98ab"; x.textAlign = "left"; x.font = "13px system-ui";
    x.fillText(`hop ${h.hop}${h.finish ? " " + h.finish : ""}`, X(h.t) + 4, P.t + 14 + ((h.hop || 0) % 3) * 15);
  }
  for (const s of RUN.seams || []) {
    x.fillStyle = s.status === "PASS" ? COL.green : s.status === "FAIL" ? COL.red : COL.grey;
    x.beginPath(); x.arc(X(s.t || 0), Y(s.tok || 0), 7, 0, 7); x.fill();
  }
  // thinking (stacked, faint) then visible
  if (pts.some((p) => p[2])) {
    x.strokeStyle = COL.violet + "aa"; x.lineWidth = 2; x.beginPath();
    pts.forEach((p, i) => (i ? x.lineTo(X(p[0]), Y(p[1] + (p[2] || 0))) : x.moveTo(X(p[0]), Y(p[1] + (p[2] || 0))))); x.stroke();
  }
  x.strokeStyle = COL.teal; x.lineWidth = 3.5; x.beginPath();
  pts.forEach((p, i) => (i ? x.lineTo(X(p[0]), Y(p[1])) : x.moveTo(X(p[0]), Y(p[1])))); x.stroke();
  x.font = "16px system-ui"; x.textAlign = "left";
  x.fillStyle = COL.teal; x.fillText("■ cumulative visible tokens", P.l + 10, P.t + 4);
  x.fillStyle = COL.violet; x.fillText("■ visible + thinking", P.l + 250, P.t + 4);
  x.fillStyle = COL.amber; x.fillText("┆ hop boundary", P.l + 430, P.t + 4);
  x.fillStyle = COL.green; x.fillText("● seam check", P.l + 570, P.t + 4);
}

// ------------------------------------------------------------------ code wall
const W_ = { code: null, v0: 0, v1: 1, sel: null, selB: null, hover: null, layout: [], drag: null, byPath: new Map() };
async function loadCode() {
  const opts = options("codes");
  const pref = opts.find((o) => o.name.startsWith("expansion")) || opts[0];
  fillSelect($("codesel"), opts, $("codesel").value, pref?.key);
  fillSelect($("failsel"), opts, $("failsel").value, pref?.key);
  if (!opts.length) { $("codesummary").textContent = "no gen/<name>/offsets.jsonl yet"; return; }
  const c = await loadKey("code", $("codesel").value);
  W_.code = c; W_.v0 = 0; W_.v1 = c.total_tok || 1; W_.sel = null; W_.selB = null;
  W_.byPath = new Map(c.files.map((f) => [f.path, f]));
  setBadges("v-code", c.__fixture);
  $("codesrc").textContent = c.__fixture ? "viewer/data/fixture" : `gen/${c.name}/offsets.jsonl · ${c.summary?.report || "no reports/" + c.name + "_code.json yet"}`;
  const s = c.summary || {};
  $("codesummary").innerHTML = `<b>${fmt(s.files)}</b> files over <b>${fmtK(c.total_tok)}</b> tokens · <span class="ok">${fmt(s.pass)} pass</span> · <span class="broken">${fmt(s.fail)} fail</span> · ${fmt(s.edges)} import edges (<span class="broken">${fmt(s.edges_broken)} broken</span>)`;
  $("codepaths").innerHTML = c.files.map((f) => `<option value="${esc(f.path)}">`).join("");
  $("fileinfo").innerHTML = `<div class="empty">Click a file on the wall</div>`; $("srcA").innerHTML = ""; $("srcB").innerHTML = "";
  drawWall();
}
$("codesel").onchange = loadCode;
const statusColor = (s) => (s === "pass" ? COL.green : s === "fail" ? COL.red : s === "warn" ? COL.amber : COL.grey);
const edgeColor = (s) => (s === "ok" ? COL.teal : s === "broken" ? COL.red : "#6b7588");
function drawWall() {
  const c = W_.code, cv = $("wall");
  if (!c || currentView !== "code") return;
  const [x, W, H] = setupCanvas(cv);
  const P = { l: 20, r: 20 }, bandY = H - 120, bandH = 46;
  const X = (t) => P.l + ((t - W_.v0) / (W_.v1 - W_.v0)) * (W - P.l - P.r);
  W_.X = X; W_.bandY = bandY; W_.bandH = bandH; W_.W = W;
  x.clearRect(0, 0, W, H);
  // axis
  x.fillStyle = "#8d98ab"; x.font = "14px system-ui"; x.textAlign = "center"; x.strokeStyle = "#2a3344";
  const span = W_.v1 - W_.v0, step = [1e3, 2e3, 5e3, 1e4, 2e4, 5e4, 1e5, 2e5].find((s) => span / s <= 12) || 2e5;
  for (let t = Math.ceil(W_.v0 / step) * step; t <= W_.v1; t += step) {
    x.beginPath(); x.moveTo(X(t), bandY + bandH + 4); x.lineTo(X(t), bandY + bandH + 12); x.stroke();
    x.fillText(fmtK(t), X(t), bandY + bandH + 28);
  }
  x.textAlign = "left"; x.fillText("token position in the stream →", P.l, H - 8);
  // buckets shading
  BUCKETS.forEach(([a, b, name], i) => {
    const xa = X(a), xb = X(Math.min(b, c.total_tok));
    if (xb < 0 || xa > W) return;
    x.fillStyle = i % 2 ? "#ffffff06" : "#ffffff0c"; x.fillRect(xa, 0, xb - xa, bandY + bandH);
    x.fillStyle = "#3d4a60"; x.font = "bold 14px system-ui"; x.fillText(name, Math.max(xa, 0) + 6, 18);
  });
  // arcs
  const sel = W_.sel;
  const maxD = Math.max(1, ...c.edges.map((e) => Math.abs(e.distance || 0)));
  for (const pass of [0, 1]) {
    for (const e of c.edges) {
      const a = W_.byPath.get(e.src), b = W_.byPath.get(e.dst);
      const ut = e.use_tok ?? a?.start_tok, dt = e.def_tok ?? b?.start_tok;
      if (ut == null || dt == null) continue;
      const on = sel && (e.src === sel.path || e.dst === sel.path);
      if ((pass === 1) !== !!on) continue;
      const xa = X(ut), xb = X(dt);
      if (Math.max(xa, xb) < 0 || Math.min(xa, xb) > W) continue;
      const hgt = Math.min(bandY - 30, 20 + (Math.abs(ut - dt) / maxD) * (bandY - 40));
      x.strokeStyle = edgeColor(e.status) + (sel ? (on ? "ff" : "18") : e.status === "broken" ? "cc" : "55");
      x.lineWidth = on ? 2.5 : e.status === "broken" ? 1.6 : 1;
      x.beginPath(); x.moveTo(xa, bandY); x.bezierCurveTo(xa, bandY - hgt * 1.33, xb, bandY - hgt * 1.33, xb, bandY); x.stroke();
    }
  }
  // bricks
  W_.layout = [];
  let lastPkg = null, lblRow = 0;
  for (const f of c.files) {
    const xa = X(f.start_tok), xb = X(f.end_tok);
    if (xb < -2 || xa > W + 2) continue;
    const w = Math.max(1.5, xb - xa - 0.6);
    x.fillStyle = statusColor(f.status);
    x.globalAlpha = sel && sel.path !== f.path && !(W_.selB && W_.selB.path === f.path) ? 0.55 : 1;
    x.fillRect(xa, bandY, w, bandH);
    x.globalAlpha = 1;
    if (sel?.path === f.path || W_.selB?.path === f.path) { x.strokeStyle = "#fff"; x.lineWidth = 2; x.strokeRect(xa - 1, bandY - 1, w + 2, bandH + 2); }
    if (W_.hover === f) { x.strokeStyle = COL.blue; x.lineWidth = 2; x.strokeRect(xa - 1, bandY - 1, w + 2, bandH + 2); }
    W_.layout.push([xa, xa + w, f]);
    if (f.pkg !== lastPkg) {
      lastPkg = f.pkg; lblRow = (lblRow + 1) % 2;
      x.fillStyle = "#c3cad6"; x.font = "13px system-ui"; x.textAlign = "left";
      x.fillRect(xa, bandY + bandH, 1, 6 + lblRow * 0);
      x.fillText(f.pkg, xa + 2, bandY + bandH + 46 + lblRow * 16);
    }
  }
}
function wallHit(e) {
  const r = $("wall").getBoundingClientRect(), mx = e.clientX - r.left, my = e.clientY - r.top;
  if (my < W_.bandY - 4 || my > W_.bandY + W_.bandH + 4) return null;
  let best = null, bd = 6;
  for (const [a, b, f] of W_.layout) { const d = mx < a ? a - mx : mx > b ? mx - b : 0; if (d < bd) { bd = d; best = f; } }
  return best;
}
$("wall").addEventListener("mousemove", (e) => {
  if (W_.drag) {
    const r = $("wall").getBoundingClientRect(), dx = e.clientX - W_.drag.x;
    const tpp = (W_.drag.v1 - W_.drag.v0) / (r.width - 40);
    const sh = -dx * tpp, total = W_.code.total_tok;
    let v0 = W_.drag.v0 + sh, v1 = W_.drag.v1 + sh;
    if (v0 < 0) { v1 -= v0; v0 = 0; } if (v1 > total) { v0 -= v1 - total; v1 = total; }
    W_.v0 = Math.max(0, v0); W_.v1 = v1; W_.drag.moved = true; drawWall(); return;
  }
  const f = wallHit(e);
  if (f !== W_.hover) { W_.hover = f; drawWall(); }
  if (f) showTip(e, `<b>${esc(f.path)}</b>\ntokens ${fmt(f.start_tok)} – ${fmt(f.end_tok)} · ${fmt(f.lines)} lines\nstatus ${esc(f.status)}${Object.keys(f.checks || {}).length ? " · " + esc(Object.keys(f.checks).join(", ")) : ""}`);
  else hideTip();
});
$("wall").addEventListener("mouseleave", () => { hideTip(); W_.hover = null; W_.drag = null; drawWall(); });
$("wall").addEventListener("mousedown", (e) => { W_.drag = { x: e.clientX, v0: W_.v0, v1: W_.v1, moved: false }; });
addEventListener("mouseup", (e) => {
  if (!W_.drag) return;
  const moved = W_.drag.moved; W_.drag = null;
  if (!moved && e.target === $("wall")) { const f = wallHit(e); if (f) selectFile(f.path); }
});
$("wall").addEventListener("wheel", (e) => {
  if (!W_.code) return;
  e.preventDefault();
  const r = $("wall").getBoundingClientRect(), fx = Math.min(1, Math.max(0, (e.clientX - r.left - 20) / (r.width - 40)));
  const at = W_.v0 + fx * (W_.v1 - W_.v0), k = Math.exp(e.deltaY * 0.0015), total = W_.code.total_tok;
  let span = Math.min(total, Math.max(2000, (W_.v1 - W_.v0) * k));
  W_.v0 = Math.max(0, Math.min(total - span, at - fx * span)); W_.v1 = W_.v0 + span; drawWall();
}, { passive: false });
$("zoomreset").onclick = () => { if (W_.code) { W_.v0 = 0; W_.v1 = W_.code.total_tok; drawWall(); } };
$("codesearch").addEventListener("change", (e) => { if (W_.byPath.has(e.target.value)) selectFile(e.target.value); });
$("longest").onclick = () => {
  const c = W_.code; if (!c) return;
  const e = c.edges.filter((x) => x.status === "ok").sort((a, b) => (b.distance || 0) - (a.distance || 0))[0]
    || c.edges.slice().sort((a, b) => (b.distance || 0) - (a.distance || 0))[0];
  if (!e) return;
  selectFile(e.dst); openSource("srcB", W_.byPath.get(e.src)); W_.selB = W_.byPath.get(e.src); drawWall();
};

async function getSource(f, c = W_.code) {
  if (c.sources?.[f.path] != null) return c.sources[f.path];
  if (f.src_url) { const r = await fetch("data/" + f.src_url + "?v=" + Date.now()); if (r.ok) return r.text(); }
  return null;
}
async function openSource(paneId, f, line) {
  const pane = $(paneId);
  if (!f) { pane.innerHTML = ""; return; }
  pane.innerHTML = `<div class="hdr">loading ${esc(f.path)}…</div>`;
  const txt = await getSource(f);
  const bad = new Map((W_.code.failures || []).filter((x) => x.path === f.path && x.line).map((x) => [+x.line, x]));
  const testCmd = /(^|\/)test_[^/]+\.py$/.test(f.path) && !W_.code.__fixture ? `<br><code>PYTHONPATH=gen/${esc(W_.code.name)}:. pytest gen/${esc(W_.code.name)}/${esc(f.path)} -q</code>` : "";
  const hdr = `<div class="hdr"><b>${esc(f.path)}</b> · tokens ${fmt(f.start_tok)}–${fmt(f.end_tok)} · <span style="color:${statusColor(f.status)}">${esc(f.status)}</span>${W_.code.__fixture ? ' · <span class="badge fixture">FIXTURE source</span>' : ""}${testCmd}</div>`;
  if (txt == null) { pane.innerHTML = hdr + `<div class="empty">source not available</div>`; return; }
  const lines = txt.split("\n"); if (lines[lines.length - 1] === "") lines.pop();
  pane.innerHTML = hdr + `<table>${lines.map((l, i) => { const b = bad.get(i + 1); return `<tr id="${paneId}-L${i + 1}" class="${b ? "bad" : ""}"${b ? ` title="${esc(b.check + ": " + b.message)}"` : ""}><td class="ln">${i + 1}</td><td>${esc(l) || " "}</td></tr>`; }).join("")}</table>`;
  const target = line || [...bad.keys()][0];
  if (target) { const row = $(`${paneId}-L${target}`); if (row) pane.scrollTop = row.offsetTop - 120; }
}
function selectFile(path, line) {
  const c = W_.code, f = W_.byPath.get(path); if (!f) return;
  W_.sel = f; W_.selB = null;
  const outE = c.edges.filter((e) => e.src === path), inE = c.edges.filter((e) => e.dst === path);
  const fl = (c.failures || []).filter((x) => x.path === path);
  const eRow = (e, other) => `<div data-p="${esc(other)}" class="${e.status === "ok" ? "ok" : e.status === "broken" ? "broken" : "unk"}">${e.status === "ok" ? "✓" : e.status === "broken" ? "✗" : "?"} ${esc(other)} <span class="unk">Δ ${fmtK(Math.abs(e.distance || 0))}</span>${e.detail ? ` <span class="unk">${esc(e.detail)}</span>` : ""}</div>`;
  $("fileinfo").innerHTML = `<div class="kv"><b>file</b> <span style="font-family:var(--mono)">${esc(f.path)}</span><br>
    <b>tokens</b> ${fmt(f.start_tok)} – ${fmt(f.end_tok)} (${fmtK(f.end_tok - f.start_tok)}) · <b>lines</b> ${fmt(f.lines)}<br>
    <b>status</b> <span style="color:${statusColor(f.status)};font-weight:800">${esc(f.status)}</span> ${Object.entries(f.checks || {}).map(([k, v]) => `<span class="v HOLD_VERIFY">${esc(k)} ${esc(v)}</span>`).join(" ")}
    ${f.terminated === false ? '<br><b class="bad">unterminated block</b>' : ""}</div>
    ${fl.length ? `<div style="margin-top:8px"><b>Failures</b>${fl.map((x) => `<div class="fail" data-line="${esc(x.line || "")}"><div class="m"><b>${esc(x.check)}</b> line ${esc(x.line ?? "?")}: ${esc(x.message)}</div></div>`).join("")}</div>` : ""}
    <div style="margin-top:8px"><b>Imports (${outE.length})</b> — click to open on the right<div class="deps">${outE.map((e) => eRow(e, e.dst)).join("") || '<span class="unk">none</span>'}</div></div>
    <div style="margin-top:8px"><b>Used by (${inE.length})</b><div class="deps">${inE.map((e) => eRow(e, e.src)).join("") || '<span class="unk">none</span>'}</div></div>`;
  $("fileinfo").querySelectorAll(".deps div[data-p]").forEach((d) => (d.onclick = () => { const g = W_.byPath.get(d.dataset.p); W_.selB = g; openSource("srcB", g); drawWall(); }));
  $("fileinfo").querySelectorAll(".fail[data-line]").forEach((d) => (d.onclick = () => openSource("srcA", f, +d.dataset.line)));
  openSource("srcA", f, line);
  $("srcB").innerHTML = "";
  // keep the selected file in view
  if (f.end_tok < W_.v0 || f.start_tok > W_.v1) { const span = W_.v1 - W_.v0; W_.v0 = Math.max(0, f.start_tok - span / 2); W_.v1 = W_.v0 + span; }
  drawWall();
}

// ------------------------------------------------------------------ failures + verifier
async function loadVerify() {
  let list = null, fix = false;
  if (S.live?.verify) { try { list = await getJSON("data/live/verify.json"); } catch {} }
  if (!list && S.fix?.verify) { try { list = await getJSON("data/fixture/verify.json"); fix = true; } catch {} }
  $("verbadges").innerHTML = !list ? "" : fix ? `<span class="badge fixture">FIXTURE — fake data</span>` : `<span class="badge real">REAL · reports/*_plan.json</span>`;
  if (!list?.length) { $("vcards").innerHTML = `<div class="panel note">No reports/*_plan.json yet (tools/verify_plan.py)</div>`; return; }
  const m = (n, l, good) => `<span class="metric"><span class="n ${good == null ? "" : good ? "good" : "bad"}">${n == null ? "–" : n}</span><span class="l">${l}</span></span>`;
  $("vcards").innerHTML = list.map((r) => {
    const x = r.metrics || {};
    if (r.kind === "acceptance") return `<div class="panel"><h3 style="margin:0">${esc(r.name)} <span class="note">${esc(r.report || "")}</span></h3>
      ${m(x.tests, "tests")}${m((x.tests ?? 0) - (x.failures ?? 0) - (x.errors ?? 0), "passed", !(x.failures || x.errors))}${m(x.failures, "failures", !x.failures)}${m(x.errors, "errors", !x.errors)}</div>`;
    const f2 = (v) => (v == null ? null : (+v).toFixed(3));
    const groups = r.groups ? "hard by check: " + Object.entries(r.groups).map(([k, v]) => `<span class="${v ? "bad" : "good"}">${esc(k)} ${v}</span>${r.soft?.[k] ? ` <span class="unk">(+${r.soft[k]} soft)</span>` : ""}`).join(" · ") : "";
    const bySrc = Object.entries(r.errors_by_src || {}).sort((a, b) => b[1] - a[1]).slice(0, 8);
    return `<div class="panel"><h3 style="margin:0">${esc(r.name)} ${r.fixture ? '<span class="badge fixture">FIXTURE</span>' : ""} <span class="note">${esc(r.report || "")}</span></h3>
      ${m(f2(x.recall), "PULL recall", x.recall == null ? null : x.recall >= 0.9)}${m(f2(x.precision), "PULL precision", x.precision == null ? null : x.precision >= 0.9)}
      ${m(x.decoys_pulled, "decoys pulled", x.decoys_pulled == null ? null : x.decoys_pulled === 0)}${m(x.hard_errors, "hard errors", x.hard_errors == null ? null : x.hard_errors === 0)}
      ${x.coverage != null ? m((100 * x.coverage).toFixed(1) + "%", "PULL facings tasked", x.coverage >= 0.999) : ""}
      ${r.classification?.labeled != null ? `<div class="note">labeled ${fmt(r.classification.labeled)} · TP ${fmt(r.classification.tp)} · FP ${fmt(r.classification.fp)} · FN ${fmt(r.classification.fn)}${r.classification.decoys != null ? " · decoys " + fmt(r.classification.decoys) : ""}</div>` : ""}
      ${groups ? `<div class="note">${groups}</div>` : ""}
      ${bySrc.length ? `<div class="note" style="margin-top:6px">errors by src: ${bySrc.map(([k, v]) => `<code>${esc(k)}</code> ${v}`).join(" · ")}</div>` : ""}
      ${(r.errors || []).slice(0, 4).map((e) => `<div class="fail" style="border-left-color:var(--amber)"><div class="p">${esc(e.src)}</div><div class="m"><b>${esc(e.group)}</b> ${esc(e.message)}</div></div>`).join("")}</div>`;
  }).join("");
  VER = list;
}
let VER = [];
const CHECK_RANK = { D2: 6, D4: 5, D1: 4, unterminated: 4, D3: 3, D6: 2 };
async function loadGallery() {
  const opts = options("codes");
  if (!opts.length) { $("gallery").innerHTML = `<div class="panel note">No code reports yet</div>`; return; }
  const c = await loadKey("code", $("failsel").value);
  setBadges("v-fail", c.__fixture);
  $("failsrc").textContent = c.__fixture ? "viewer/data/fixture" : (c.summary?.report || "no reports/" + c.name + "_code.json yet (statuses unknown)");
  const byPath = new Map(c.files.map((f) => [f.path, f]));
  const fails = (c.failures || []).map((x) => ({ ...x, layer: "L1" }));
  for (const r of VER.filter((r) => r.name === c.name)) for (const e of r.errors || []) {      // Layer 2 plan errors of the same drill, mapped to code by src
    const f = byPath.get(e.src); if (!f) continue;
    fails.push({ check: "L2 " + (e.group || ""), path: e.src, line: null, message: e.message, tok: f.start_tok, layer: "L2", severity: 3 });
  }
  const srcCache = new Map();
  const getSrc = async (f) => { if (!srcCache.has(f.path)) srcCache.set(f.path, await getSource(f, c).catch(() => null)); return srcCache.get(f.path); };
  const cols = await Promise.all(BUCKETS.map(async ([a, b, name]) => {
    const files = c.files.filter((f) => f.start_tok >= a && f.start_tok < b);
    const bad = files.filter((f) => f.status === "fail").length;
    const items = fails.filter((x) => (x.tok ?? byPath.get(x.path)?.start_tok ?? -1) >= a && (x.tok ?? byPath.get(x.path)?.start_tok ?? -1) < b)
      .sort((p, q) => (q.severity || 0) - (p.severity || 0) || (CHECK_RANK[q.check] || 1) - (CHECK_RANK[p.check] || 1)).slice(0, 6);
    const cards = await Promise.all(items.map(async (x) => {
      const f = byPath.get(x.path);
      let snip = "";
      if (f && x.line) {
        const t = await getSrc(f);
        if (t) {
          const L = t.split("\n"), i = x.line - 1;
          snip = L.slice(Math.max(0, i - 2), i + 3).map((l, j) => { const n = Math.max(0, i - 2) + j + 1; const s = `${String(n).padStart(4)}  ${esc(l)}`; return n === x.line ? `<span class="hl">${s}</span>` : s; }).join("\n");
        }
      }
      return `<div class="fail" data-p="${esc(x.path)}" data-line="${esc(x.line ?? "")}" style="${x.layer === "L2" ? "border-left-color:var(--amber)" : ""}">
        <div class="p">${esc(x.path)}${x.line ? ":" + x.line : ""} · tok ${fmtK(x.tok ?? f?.start_tok ?? 0)}</div>
        <div class="m"><b>${esc(x.check)}</b> ${esc(x.message)}</div>${snip ? `<pre>${snip}</pre>` : ""}</div>`;
    }));
    return `<div class="panel bucket"><h3>${name}</h3><div class="rate">${files.length} files · <span class="${bad ? "bad" : "good"}">${bad} failing (${files.length ? ((100 * bad) / files.length).toFixed(0) : 0}%)</span> · ${fails.filter((x) => (x.tok ?? -1) >= a && (x.tok ?? -1) < b).length} findings</div>
      ${cards.join("") || '<div class="note">no failures in this bucket</div>'}</div>`;
  }));
  $("gallery").innerHTML = cols.join("");
  $("gallery").querySelectorAll(".fail[data-p]").forEach((d) => (d.onclick = async () => {
    if ($("codesel").value !== $("failsel").value) { $("codesel").value = $("failsel").value; await loadCode(); }
    show("code"); selectFile(d.dataset.p, +d.dataset.line || undefined);
  }));
}
$("failsel").onchange = loadGallery;

// ------------------------------------------------------------------ boot + reload
async function loadAll() {
  await loadIndexes();
  const jobs = [loadDrill(), loadRun(), loadCode().then(loadVerify).then(loadGallery)];
  for (const j of jobs) await j.catch((e) => console.error(e));
}
$("reload").onclick = loadAll;
let lastBuilt = null;
setInterval(async () => {
  if (!$("autoref").checked || R.playing) return;
  try { const i = await getJSON("data/live/index.json"); if (lastBuilt && i.sig !== lastBuilt) await loadAll(); lastBuilt = i.sig; } catch {}
}, 5000);
addEventListener("resize", () => { drawHops(); drawWall(); });
(async () => {
  await loadAll();
  lastBuilt = S.live?.sig || null;
  let v = "map"; try { v = localStorage.getItem("rs_view") || "map"; } catch {}
  show(VIEWS.includes(v) ? v : "map");
  requestAnimationFrame(tick);
})();
