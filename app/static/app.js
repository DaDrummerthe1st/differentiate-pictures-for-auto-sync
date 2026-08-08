let downloadsInProgress = 0;
window.addEventListener("beforeunload", (e) => {
  if (downloadsInProgress > 0) {
    e.preventDefault();
    e.returnValue = "";
  }
});

function logEvent(type, detail) {
  fetch("/api/event", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type, detail: detail == null ? "" : String(detail) }),
  }).catch(() => {});
}

// The session's access-token cookie is short-lived (5min, see
// server/app/tokens.py) so it can be silently renewed via the
// httponly refresh cookie without disrupting a browsing session. Only
// on a *second* 401 (refresh itself failed - refresh cookie expired
// after 12h, or was revoked by a logout elsewhere) do we bounce to the
// login page, since at that point there's no session left to recover.
let _refreshInFlight = null;

async function authFetch(url, options) {
  const res = await fetch(url, options);
  if (res.status !== 401) return res;

  if (!_refreshInFlight) {
    _refreshInFlight = fetch("/refresh", { method: "POST" }).finally(() => {
      _refreshInFlight = null;
    });
  }
  const refreshRes = await _refreshInFlight;
  if (!refreshRes.ok) {
    window.location.href = "/login";
    return res;
  }
  return fetch(url, options);
}

// Real user activity only - not just "the tab is open" - so a browser
// left open and unattended doesn't stay logged in forever just because
// the proactive refresh below would otherwise keep renewing it forever.
let lastActivityAt = Date.now();
["mousemove", "keydown", "click", "scroll", "touchstart"].forEach((evt) =>
  window.addEventListener(evt, () => (lastActivityAt = Date.now()), { passive: true })
);

// ?test_idle_ms overrides this for Selenium tests, which can't wait out
// the real 30 minutes.
const IDLE_TIMEOUT_MS =
  Number(new URLSearchParams(location.search).get("test_idle_ms")) || 30 * 60 * 1000;

function silentRefresh() {
  if (Date.now() - lastActivityAt > IDLE_TIMEOUT_MS) return;
  if (_refreshInFlight) return;
  _refreshInFlight = fetch("/refresh", { method: "POST" }).finally(() => {
    _refreshInFlight = null;
  });
}

// Proactively renews the access-token cookie before it expires, so a
// long browsing session never actually hits an expired token in normal
// use - this is what keeps plain <img> thumbnail/lightbox loads working
// (they can't go through authFetch's reactive refresh-and-retry at
// all, since they're not fetch() calls). ?test_refresh_ms overrides the
// interval for Selenium tests, which can't wait out the real ~4 minutes.
const SILENT_REFRESH_INTERVAL_MS =
  Number(new URLSearchParams(location.search).get("test_refresh_ms")) || 4 * 60 * 1000;

// --- Dismissable info messages: "don't show again" hides them from
// auto-popping-up, but every message stays reachable via the Hjälp
// button so nothing read-once is ever permanently lost. ---
const INFO_MESSAGES = {
  voiceover: {
    title: "Så fungerar berättelseinspelning",
    body:
      "Tryck på inspelningsknappen för att börja spela in ljud. Bläddra och peka " +
      "fritt på bilderna medan du pratar - var du pekar sparas tillsammans med " +
      "ljudet, så när berättelsen spelas upp igen visas rätt bild och pekpunkt i " +
      "takt med rösten. Tryck på \"Stoppa inspelning\" när du är klar.",
  },
};

function dismissedInfoSet() {
  try {
    return new Set(JSON.parse(localStorage.getItem("mpv_dismissed_info") || "[]"));
  } catch (e) {
    return new Set();
  }
}

function showInfo(key) {
  const info = INFO_MESSAGES[key];
  if (!info) return;
  document.getElementById("infoModalTitle").textContent = info.title;
  document.getElementById("infoModalBody").textContent = info.body;
  document.getElementById("infoModalDontShowAgain").checked = dismissedInfoSet().has(key);
  const modal = document.getElementById("infoModal");
  modal.dataset.key = key;
  modal.classList.remove("hidden");
}

function closeInfoModal() {
  const modal = document.getElementById("infoModal");
  const key = modal.dataset.key;
  const dontShow = document.getElementById("infoModalDontShowAgain").checked;
  const dismissed = dismissedInfoSet();
  if (dontShow) dismissed.add(key);
  else dismissed.delete(key);
  localStorage.setItem("mpv_dismissed_info", JSON.stringify(Array.from(dismissed)));
  modal.classList.add("hidden");
  return key;
}

function maybeShowInfo(key, onProceed) {
  if (dismissedInfoSet().has(key)) {
    if (onProceed) onProceed();
    return;
  }
  showInfo(key);
  document.getElementById("infoModal").dataset.onProceed = "1";
  pendingInfoProceed = onProceed || null;
}

let pendingInfoProceed = null;

document.getElementById("infoModalClose").addEventListener("click", () => {
  closeInfoModal();
  if (pendingInfoProceed) {
    const fn = pendingInfoProceed;
    pendingInfoProceed = null;
    fn();
  }
});

document.getElementById("helpBtn").addEventListener("click", () => {
  const container = document.getElementById("helpModalItems");
  container.innerHTML = "";
  for (const [key, info] of Object.entries(INFO_MESSAGES)) {
    const btn = document.createElement("button");
    btn.textContent = info.title;
    btn.addEventListener("click", () => {
      document.getElementById("helpModal").classList.add("hidden");
      showInfo(key);
    });
    container.appendChild(btn);
  }
  document.getElementById("helpModal").classList.remove("hidden");
});
document.getElementById("helpModalClose").addEventListener("click", () => {
  document.getElementById("helpModal").classList.add("hidden");
});

const DB_NAME = "mamma-photo-viewer";
const STORE = "handles";

function idbOpen() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(STORE);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function idbGet(key) {
  const db = await idbOpen();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, "readonly");
    const req = tx.objectStore(STORE).get(key);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function idbSet(key, value) {
  const db = await idbOpen();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, "readwrite");
    tx.objectStore(STORE).put(value, key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

let downloadDirHandle = null;
const usedNames = new Set();

async function uniqueFileHandle(dirHandle, filename) {
  let name = filename;
  let i = 2;
  while (usedNames.has(name)) {
    const dot = filename.lastIndexOf(".");
    name = dot === -1 ? `${filename}_${i}` : `${filename.slice(0, dot)}_${i}${filename.slice(dot)}`;
    i++;
  }
  usedNames.add(name);
  return dirHandle.getFileHandle(name, { create: true });
}

async function saveImage(relpath) {
  await maybeOfferFolderPicker();
  if (downloadDirHandle) {
    const res = await authFetch(`/original?p=${encodeURIComponent(relpath)}`);
    if (!res.ok) throw new Error("download failed: " + relpath);
    const blob = await res.blob();
    const filename = relpath.split("/").pop();
    // getFileHandle(create: true) creates the (empty) file on disk
    // immediately, before any bytes are written - if write/close fails
    // afterward (e.g. a USB drive dropping mid-write), clean up the
    // orphaned empty file and free the name instead of leaving debris.
    const fileHandle = await uniqueFileHandle(downloadDirHandle, filename);
    try {
      const writable = await fileHandle.createWritable();
      await writable.write(blob);
      await writable.close();
    } catch (e) {
      usedNames.delete(fileHandle.name);
      try {
        await downloadDirHandle.removeEntry(fileHandle.name);
      } catch (removeErr) {
        // best-effort - nothing more we can do if removal itself fails
      }
      throw e;
    }
  } else {
    const filename = relpath.split("/").pop();
    const a = document.createElement("a");
    a.href = `/original?p=${encodeURIComponent(relpath)}`;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }
  logEvent("image_download", relpath);
}

function setBtnProgress(btn, pct, text) {
  btn.textContent = text;
  btn.style.background =
    pct == null ? "" : `linear-gradient(to right, #1f8f3f ${pct}%, #34c759 ${pct}%)`;
}

// Bulk downloads go file-by-file rather than as one big zip: over a slow
// or unreliable link, a single giant zip is all-or-nothing (any hiccup
// loses the whole batch, and there's no way to see real progress until
// it's fully built). Per-file downloads show honest incremental
// progress, can be cancelled without losing what's already saved, and a
// single failed/corrupt file doesn't take down the rest.
let bulkDownloadActive = false;
let bulkDownloadCancelled = false;

function updateCancelDownloadBtn(show) {
  document.getElementById("cancelDownloadBtn").classList.toggle("hidden", !show);
}

async function downloadFilesSequentially(paths, btn) {
  if (bulkDownloadActive) return;
  bulkDownloadActive = true;
  bulkDownloadCancelled = false;
  const original = btn.textContent;
  const originalBg = btn.style.background;
  btn.disabled = true;
  downloadsInProgress++;
  updateCancelDownloadBtn(true);

  // A long download can otherwise get silently paused if the screen
  // sleeps or the OS suspends the tab - the wake lock reduces (doesn't
  // guarantee, browsers can still ignore it) that risk while active.
  let wakeLock = null;
  try {
    if ("wakeLock" in navigator) wakeLock = await navigator.wakeLock.request("screen");
  } catch (e) {
    // not fatal - downloads still work without it, just more exposed
    // to the tab/screen sleeping mid-transfer
  }

  let saved = 0;
  let failed = 0;
  for (let i = 0; i < paths.length; i++) {
    if (bulkDownloadCancelled) break;
    const filename = paths[i].split("/").pop();
    const pct = Math.round(((i + 1) / paths.length) * 100);
    setBtnProgress(btn, pct, `${pct}% - ${i + 1}/${paths.length}: ${filename}`);
    try {
      await saveImage(paths[i]);
      saved++;
    } catch (e) {
      failed++;
    }
  }

  if (wakeLock) {
    try {
      await wakeLock.release();
    } catch (e) {
      // already released (e.g. tab lost visibility) - nothing to do
    }
  }
  updateCancelDownloadBtn(false);
  if (bulkDownloadCancelled) {
    setBtnProgress(btn, null, `Avbruten - ${saved} av ${paths.length} sparade`);
    logEvent("download_cancelled", `saved=${saved} of=${paths.length}`);
  } else {
    setBtnProgress(
      btn,
      100,
      failed ? `Klart! ${saved} sparade, ${failed} misslyckades` : `Klart! ${saved} sparade`
    );
    logEvent("download_done", `saved=${saved} failed=${failed} of=${paths.length}`);
  }
  downloadsInProgress--;
  bulkDownloadActive = false;
  setTimeout(() => {
    btn.style.background = originalBg;
    btn.textContent = original;
    btn.disabled = false;
  }, 4000);
}

document.getElementById("cancelDownloadBtn").addEventListener("click", () => {
  bulkDownloadCancelled = true;
});

const FOLDER_PROMPT_DONE_KEY = "mpv_folder_prompt_done";

async function pickDownloadFolder() {
  try {
    const handle = await window.showDirectoryPicker({ mode: "readwrite" });
    downloadDirHandle = handle;
    await primeUsedNames();
    updateDownloadFolderLabel();
    logEvent("folder_picked", handle.name || "");
    try {
      await idbSet("dir", handle);
    } catch (e) {
      // best-effort persistence only - losing this just means the
      // folder won't auto-restore on the next visit, not a functional
      // failure right now
    }
    return true;
  } catch (e) {
    logEvent("folder_skipped");
    return false;
  }
}

// Offered once, lazily, on the first actual save action rather than
// blocking the gallery upfront - see documentation/gui/TODO.md's
// "Download-folder UX rework". "Once" is remembered forever via
// localStorage so a decline/cancel doesn't nag on every download;
// re-picking afterward only happens via the toolbar label click.
async function maybeOfferFolderPicker() {
  if (downloadDirHandle) return;
  if (localStorage.getItem(FOLDER_PROMPT_DONE_KEY)) return;
  localStorage.setItem(FOLDER_PROMPT_DONE_KEY, "1");
  if (typeof window.showDirectoryPicker !== "function") return;
  await pickDownloadFolder();
}

function updateDownloadFolderLabel() {
  const label = document.getElementById("downloadFolderLabel");
  if (downloadDirHandle) {
    // The File System Access API never exposes a full filesystem path
    // (deliberate browser privacy sandboxing) - only the picked
    // folder's own name is ever available, so that's all the hover
    // title can show too.
    const name = downloadDirHandle.name || "vald mapp";
    label.textContent = "Bilder sparas i: " + name;
    label.title = name;
  } else {
    label.textContent = "Nedladdningar sparas enligt webbläsarens nedladdningsinställning";
    label.removeAttribute("title");
  }
}

async function tryRestoreDownloadFolder() {
  let handle;
  try {
    handle = await idbGet("dir");
  } catch (e) {
    return false;
  }
  if (!handle) return false;
  const perm = await handle.queryPermission({ mode: "readwrite" });
  if (perm === "granted") {
    downloadDirHandle = handle;
    return true;
  }
  return false;
}

async function primeUsedNames() {
  usedNames.clear();
  for await (const entry of downloadDirHandle.values()) {
    if (entry.kind === "file") usedNames.add(entry.name);
  }
}

async function enterGallery() {
  if (downloadDirHandle) {
    await primeUsedNames();
  }
  updateDownloadFolderLabel();
  loadTree();
  setInterval(silentRefresh, SILENT_REFRESH_INTERVAL_MS);
}

let selectMode = false;
const marked = new Set();
let allImages = [];
let currentLightboxIndex = -1;

// Only one album is ever shown at a time - the nav-pill bar switches
// which one, instead of the old scroll-to-it behavior. Persisted so a
// reload lands back on the same album rather than always resetting to
// the first one.
let activeHeadline = localStorage.getItem("mpv_active_headline") || null;

function setActiveAlbum(headline) {
  activeHeadline = headline;
  localStorage.setItem("mpv_active_headline", headline);
  document.querySelectorAll(".nav-pill").forEach((pill) => {
    pill.classList.toggle("current", pill.dataset.headline === headline);
  });
  renderActiveAlbum();
  logEvent("nav_jump", headline);
}

let allSections = [];
// Global index (into allImages) that each album's first image starts at -
// needed so a thumbnail built while only the active album is in the DOM
// still gets the same dataset.idx it would have in a full render, since
// the lightbox's prev/next intentionally still spans every album, not
// just the active one (see TODO.md).
let sectionImageOffset = new Map();

function renderTree(sections) {
  allSections = sections;

  if (!sections.some((s) => s.headline === activeHeadline)) {
    activeHeadline = sections.length > 0 ? sections[0].headline : null;
    if (activeHeadline) localStorage.setItem("mpv_active_headline", activeHeadline);
  }

  allImages = [];
  sectionImageOffset = new Map();
  for (const section of sections) {
    sectionImageOffset.set(section.headline, allImages.length);
    for (const chunk of section.chunks) {
      for (const img of chunk.images) allImages.push(img);
    }
  }

  const nav = document.getElementById("albumNav");
  nav.innerHTML = "";
  for (const section of sections) {
    const pill = document.createElement("button");
    pill.className = "nav-pill" + (section.headline === activeHeadline ? " current" : "");
    pill.dataset.headline = section.headline;
    pill.textContent = section.headline;
    pill.addEventListener("click", () => setActiveAlbum(section.headline));
    nav.appendChild(pill);
  }

  renderActiveAlbum();
}

// Only the active album's DOM (and thumbnail <img> elements) ever exist -
// switching albums tears this down and rebuilds it, rather than keeping
// every album in the DOM and hiding the inactive ones with CSS, so a
// hidden album costs nothing (no nodes, no thumbnail requests).
function renderActiveAlbum() {
  const tree = document.getElementById("tree");
  tree.innerHTML = "";
  const section = allSections.find((s) => s.headline === activeHeadline);
  if (!section) return;

  let idx = sectionImageOffset.get(section.headline) ?? 0;

  const album = document.createElement("div");
  album.className = "album";
  album.dataset.headline = section.headline;

  const h = document.createElement("h2");
  h.className = "headline";
  h.textContent = section.headline;
  album.appendChild(h);

  const body = document.createElement("div");
  body.className = "album-body";

  for (const chunk of section.chunks) {
    const ct = document.createElement("div");
    ct.className = "chunk-title";
    ct.textContent = chunk.path;
    body.appendChild(ct);
    const grid = document.createElement("div");
    grid.className = "grid";
    for (const img of chunk.images) {
      const thumb = document.createElement("div");
      thumb.className = "thumb";
      thumb.dataset.path = img;
      thumb.dataset.idx = idx;
      idx += 1;
      const imgEl = document.createElement("img");
      imgEl.loading = "lazy";
      imgEl.src = `/thumb?p=${encodeURIComponent(img)}`;
      thumb.appendChild(imgEl);
      thumb.addEventListener("click", () => onThumbClick(thumb));
      grid.appendChild(thumb);
    }
    body.appendChild(grid);
  }
  album.appendChild(body);
  tree.appendChild(album);
}

function onThumbClick(thumbEl) {
  const path = thumbEl.dataset.path;
  if (selectMode) {
    if (marked.has(path)) {
      marked.delete(path);
      thumbEl.classList.remove("marked");
      logEvent("image_unmark", path);
    } else {
      marked.add(path);
      thumbEl.classList.add("marked");
      logEvent("image_mark", path);
    }
    updateDownloadSelectedBtn();
  } else {
    openLightbox(parseInt(thumbEl.dataset.idx, 10));
  }
}

function updateDownloadSelectedBtn() {
  const btn = document.getElementById("downloadSelectedBtn");
  if (marked.size > 0) {
    btn.textContent = `Ladda ner markerade (${marked.size})`;
    btn.classList.remove("hidden");
  } else {
    btn.classList.add("hidden");
  }
}

document.getElementById("downloadAllBtn").addEventListener("click", () => {
  logEvent("download_all", `count=${allImages.length}`);
  downloadFilesSequentially(allImages, document.getElementById("downloadAllBtn"));
});

document.getElementById("albumNavToggle").addEventListener("click", () => {
  const bar = document.getElementById("albumNavBar");
  const expanded = bar.classList.toggle("expanded");
  document.getElementById("albumNavToggle").textContent = expanded
    ? "Visa färre ▴"
    : "Visa alla album ▾";
});

document.getElementById("gridSizeBtn").addEventListener("click", () => {
  const large = document.body.classList.toggle("large-thumbs");
  document.getElementById("gridSizeBtn").textContent = large ? "Små bilder" : "Stora bilder";
  localStorage.setItem("mpv_large_thumbs", large ? "1" : "0");
  logEvent("grid_size", large ? "large" : "normal");
});
if (localStorage.getItem("mpv_large_thumbs") === "1") {
  document.body.classList.add("large-thumbs");
  document.getElementById("gridSizeBtn").textContent = "Små bilder";
}

document.getElementById("selectModeBtn").addEventListener("click", () => {
  selectMode = !selectMode;
  const btn = document.getElementById("selectModeBtn");
  btn.classList.toggle("active", selectMode);
  btn.textContent = selectMode ? "Markeringsläge PÅ" : "Markera bilder";
  logEvent("select_mode", selectMode ? "on" : "off");
  if (!selectMode) {
    marked.clear();
    document.querySelectorAll(".thumb.marked").forEach((el) => el.classList.remove("marked"));
    updateDownloadSelectedBtn();
  }
});

document.getElementById("downloadSelectedBtn").addEventListener("click", async () => {
  const paths = Array.from(marked);
  logEvent("download_selected", `count=${paths.length}`);
  await downloadFilesSequentially(paths, document.getElementById("downloadSelectedBtn"));
  marked.clear();
  document.querySelectorAll(".thumb.marked").forEach((el) => el.classList.remove("marked"));
  updateDownloadSelectedBtn();
});

// --- Freeform voiceover recording: talk while browsing, track which
// picture and where on it the mouse points, without a fixed plan. ---
let lastMouseX = 0;
let lastMouseY = 0;
document.addEventListener("mousemove", (e) => {
  lastMouseX = e.clientX;
  lastMouseY = e.clientY;
});

let voiceoverActive = false;
let voiceoverRecorder = null;
let voiceoverChunks = [];
let voiceoverEvents = [];
let voiceoverStartMs = 0;
let voiceoverSampleTimer = null;

function currentPointedImage() {
  const el = document.elementFromPoint(lastMouseX, lastMouseY);
  if (!el) return null;
  if (el.id === "lbImg" && !document.getElementById("lightbox").classList.contains("hidden")) {
    return { imgEl: el, path: allImages[currentLightboxIndex] };
  }
  const thumbEl = el.closest && el.closest(".thumb");
  if (thumbEl) {
    return { imgEl: thumbEl.querySelector("img"), path: thumbEl.dataset.path };
  }
  return null;
}

function sampleVoiceoverPointer() {
  const target = currentPointedImage();
  if (!target || !target.imgEl || !target.path) return;
  const rect = target.imgEl.getBoundingClientRect();
  if (rect.width === 0 || rect.height === 0) return;
  const xFrac = (lastMouseX - rect.left) / rect.width;
  const yFrac = (lastMouseY - rect.top) / rect.height;
  if (xFrac < 0 || xFrac > 1 || yFrac < 0 || yFrac > 1) return;
  const t = (Date.now() - voiceoverStartMs) / 1000;
  voiceoverEvents.push({
    t: Math.round(t * 10) / 10,
    path: target.path,
    x: Math.round(xFrac * 1000) / 1000,
    y: Math.round(yFrac * 1000) / 1000,
  });
}

function updateVoiceoverUI() {
  document.getElementById("recordingBanner").classList.toggle("hidden", !voiceoverActive);
  document.getElementById("voiceoverRecordBtn").classList.toggle("hidden", voiceoverActive);
}

async function uploadVoiceover() {
  const blob = new Blob(voiceoverChunks, { type: "audio/webm" });
  const form = new FormData();
  form.append("audio", blob, "voiceover.webm");
  form.append("events", JSON.stringify(voiceoverEvents));
  try {
    await authFetch("/api/voiceover", { method: "POST", body: form });
    logEvent("voiceover_saved", `events=${voiceoverEvents.length}`);
  } catch (e) {
    logEvent("voiceover_upload_error", String(e));
  }
}

async function startVoiceover() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Mikrofon stöds inte i den här webbläsaren.");
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    voiceoverChunks = [];
    voiceoverEvents = [];
    voiceoverStartMs = Date.now();
    voiceoverRecorder = new MediaRecorder(stream);
    voiceoverRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) voiceoverChunks.push(e.data);
    };
    voiceoverRecorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      clearInterval(voiceoverSampleTimer);
      await uploadVoiceover();
    };
    voiceoverRecorder.start();
    voiceoverSampleTimer = setInterval(sampleVoiceoverPointer, 200);
    voiceoverActive = true;
    updateVoiceoverUI();
    logEvent("voiceover_start");
  } catch (e) {
    alert("Kunde inte komma åt mikrofonen: " + e.message);
  }
}

function stopVoiceover() {
  if (voiceoverRecorder && voiceoverRecorder.state === "recording") {
    voiceoverRecorder.stop();
  }
  voiceoverActive = false;
  updateVoiceoverUI();
}

document.getElementById("voiceoverRecordBtn").addEventListener("click", () => {
  maybeShowInfo("voiceover", startVoiceover);
});
document.getElementById("voiceoverStopBtn").addEventListener("click", stopVoiceover);

async function openVoiceoverList() {
  const modal = document.getElementById("voiceoverListModal");
  const container = document.getElementById("voiceoverListItems");
  container.textContent = "Laddar...";
  modal.classList.remove("hidden");
  const res = await authFetch("/api/voiceovers");
  const items = await res.json();
  container.innerHTML = "";
  if (items.length === 0) {
    container.textContent = "Inga berättelser inspelade ännu.";
    return;
  }
  for (const item of items) {
    const row = document.createElement("div");
    row.className = "voiceover-item";
    const label = document.createElement("span");
    const date = new Date(item.ts);
    const stockholmTime = date.toLocaleString("sv-SE", { timeZone: "Europe/Stockholm" });
    label.textContent = `${stockholmTime} — ${item.image_count} bilder`;
    const playBtn = document.createElement("button");
    playBtn.textContent = "Spela upp";
    playBtn.addEventListener("click", () => openVoiceoverPlayer(item.id));
    row.appendChild(label);
    row.appendChild(playBtn);
    container.appendChild(row);
  }
}
document.getElementById("voiceoverListBtn").addEventListener("click", openVoiceoverList);
document.getElementById("voiceoverListClose").addEventListener("click", () => {
  document.getElementById("voiceoverListModal").classList.add("hidden");
});

let playerEvents = [];
async function openVoiceoverPlayer(id) {
  document.getElementById("voiceoverListModal").classList.add("hidden");
  const res = await authFetch(`/api/voiceover/${id}`);
  const data = await res.json();
  playerEvents = data.events || [];
  const audio = document.getElementById("voiceoverPlayerAudio");
  audio.src = data.audio_url;
  document.getElementById("voiceoverPlayer").classList.remove("hidden");
  document.getElementById("voiceoverPointerDot").classList.add("hidden");
  audio.currentTime = 0;
  audio.play();
  logEvent("voiceover_played", String(id));
}
document.getElementById("voiceoverPlayerClose").addEventListener("click", () => {
  const audio = document.getElementById("voiceoverPlayerAudio");
  audio.pause();
  document.getElementById("voiceoverPlayer").classList.add("hidden");
});
document.getElementById("voiceoverPlayerAudio").addEventListener("timeupdate", (e) => {
  if (playerEvents.length === 0) return;
  const t = e.target.currentTime;
  let ev = playerEvents[0];
  for (const candidate of playerEvents) {
    if (candidate.t <= t) ev = candidate;
    else break;
  }
  const img = document.getElementById("voiceoverPlayerImg");
  const wantedSrc = `/original?p=${encodeURIComponent(ev.path)}`;
  if (!img.src.endsWith(wantedSrc)) img.src = wantedSrc;
  const dot = document.getElementById("voiceoverPointerDot");
  dot.classList.remove("hidden");
  dot.style.left = ev.x * 100 + "%";
  dot.style.top = ev.y * 100 + "%";
});

function openLightbox(idx) {
  currentLightboxIndex = idx;
  const lb = document.getElementById("lightbox");
  document.getElementById("lbImg").src = `/original?p=${encodeURIComponent(allImages[idx])}`;
  lb.classList.remove("hidden");
  logEvent("image_view", allImages[idx]);
  loadTagsForCurrentPhoto();
}
function closeLightbox() {
  document.getElementById("lightbox").classList.add("hidden");
  closeTagForm();
  disarmDrawBox();
}
function lightboxStep(delta) {
  currentLightboxIndex = (currentLightboxIndex + delta + allImages.length) % allImages.length;
  document.getElementById("lbImg").src = `/original?p=${encodeURIComponent(allImages[currentLightboxIndex])}`;
  logEvent("image_view", allImages[currentLightboxIndex]);
  closeTagForm();
  disarmDrawBox();
  loadTagsForCurrentPhoto();
}

document.getElementById("lbClose").addEventListener("click", closeLightbox);
document.getElementById("lbPrev").addEventListener("click", () => lightboxStep(-1));
document.getElementById("lbNext").addEventListener("click", () => lightboxStep(1));
document.getElementById("lbDownload").addEventListener("click", async (e) => {
  const btn = e.currentTarget;
  const original = btn.textContent;
  btn.textContent = "Sparar...";
  try {
    await saveImage(allImages[currentLightboxIndex]);
    btn.textContent = "Sparad!";
  } catch (err) {
    btn.textContent = "Fel!";
  }
  setTimeout(() => (btn.textContent = original), 1200);
});
document.addEventListener("keydown", (e) => {
  if (!document.getElementById("tagForm").classList.contains("hidden")) {
    // A form field may have focus (typing a tag's value) - only Escape is
    // ours to handle here; everything else (arrow keys moving the text
    // cursor, etc.) must not also step the lightbox underneath.
    if (e.key === "Escape") closeTagForm();
    return;
  }
  if (drawPhase !== "idle" && e.key === "Escape") {
    disarmDrawBox();
    return;
  }
  if (document.getElementById("lightbox").classList.contains("hidden")) return;
  if (e.key === "Escape") closeLightbox();
  else if (e.altKey && e.key === "ArrowLeft") {
    e.preventDefault();
    closeLightbox();
  } else if (e.key === "ArrowLeft") lightboxStep(-1);
  else if (e.key === "ArrowRight") lightboxStep(1);
});

// ---- Tags: automatic (future), user-changeable, and user-set (manual
// bounding box or whole-photo) - see documentation/tags/TAXONOMY.md for the
// full category model this is a narrowed, build-ready slice of. ----

const TAG_CATEGORY_LABELS = {
  people: "Person",
  places: "Plats",
  objects: "Föremål",
  animals: "Djur",
  occasion: "Tillfälle",
  generic: "Övrigt",
};

// Shown under the category picker for categories where it materially
// changes what a user should draw/type - not every category needs one.
const TAG_CATEGORY_HINTS = {
  people:
    "Tips: rita helst bara runt ansiktet, med en jämn marginal - det ger både ett resultat som är " +
    "lättare att träffa exakt och bättre indata den dag en modell ska tränas på dina rutor.",
};

let currentPhotoTags = [];
let tagFormMode = null; // "create" | "edit"
let tagFormEditingId = null;
let tagFormPendingBox = null; // {x,y,w,h} fractions, or null for a whole-photo tag

function clamp01(n) {
  return Math.max(0, Math.min(1, n));
}

async function loadTagsForCurrentPhoto() {
  const path = allImages[currentLightboxIndex];
  const res = await authFetch(`/api/tags?p=${encodeURIComponent(path)}`);
  currentPhotoTags = res.ok ? await res.json() : [];
  renderTagOverlay();
}

function renderTagOverlay() {
  const boxesWrap = document.getElementById("lbBoxes");
  const chipsWrap = document.getElementById("lbTagChips");
  boxesWrap.innerHTML = "";
  chipsWrap.innerHTML = "";
  for (const tag of currentPhotoTags) {
    if (tag.bbox) {
      const box = document.createElement("div");
      box.className = "tag-box" + (tag.source === "auto" ? " tag-box-auto" : "");
      box.style.left = tag.bbox.x * 100 + "%";
      box.style.top = tag.bbox.y * 100 + "%";
      box.style.width = tag.bbox.w * 100 + "%";
      box.style.height = tag.bbox.h * 100 + "%";
      const label = document.createElement("span");
      label.className = "tag-box-label";
      label.textContent = tag.value;
      box.appendChild(label);
      box.addEventListener("mousedown", (e) => e.stopPropagation());
      box.addEventListener("touchstart", (e) => e.stopPropagation());
      box.addEventListener("click", () => openTagForm({ mode: "edit", tag }));
      boxesWrap.appendChild(box);
    } else {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "tag-chip" + (tag.source === "auto" ? " tag-chip-auto" : "");
      chip.textContent = `${TAG_CATEGORY_LABELS[tag.category] || tag.category}: ${tag.value}`;
      chip.addEventListener("click", () => openTagForm({ mode: "edit", tag }));
      chipsWrap.appendChild(chip);
    }
  }
}

async function loadTagValueSuggestions(category) {
  const res = await authFetch(`/api/tags/values?category=${encodeURIComponent(category)}`);
  const values = res.ok ? await res.json() : [];
  const list = document.getElementById("tagValueSuggestions");
  list.innerHTML = "";
  for (const v of values) {
    const opt = document.createElement("option");
    opt.value = v;
    list.appendChild(opt);
  }
}

function updateTagCategoryHint(category) {
  const hint = document.getElementById("tagCategoryHint");
  const text = TAG_CATEGORY_HINTS[category];
  if (text) {
    hint.textContent = text;
    hint.classList.remove("hidden");
  } else {
    hint.classList.add("hidden");
  }
}

function openTagForm({ mode, tag = null, pendingBox = null }) {
  disarmDrawBox();
  tagFormMode = mode;
  tagFormEditingId = tag ? tag.id : null;
  tagFormPendingBox = tag ? tag.bbox : pendingBox;
  document.getElementById("tagFormTitle").textContent = mode === "edit" ? "Redigera tagg" : "Ny tagg";
  const categorySelect = document.getElementById("tagCategorySelect");
  categorySelect.value = tag ? tag.category : pendingBox ? "people" : "places";
  document.getElementById("tagValueInput").value = tag ? tag.value : "";
  document.getElementById("tagFormDelete").classList.toggle("hidden", mode !== "edit");
  updateTagCategoryHint(categorySelect.value);
  loadTagValueSuggestions(categorySelect.value);
  document.getElementById("tagForm").classList.remove("hidden");
  document.getElementById("tagValueInput").focus();
}

function closeTagForm() {
  document.getElementById("tagForm").classList.add("hidden");
  tagFormMode = null;
  tagFormEditingId = null;
  tagFormPendingBox = null;
}

document.getElementById("lbAddTagBtn").addEventListener("click", () => {
  openTagForm({ mode: "create", pendingBox: null });
});
document.getElementById("tagCategorySelect").addEventListener("change", (e) => {
  loadTagValueSuggestions(e.target.value);
  updateTagCategoryHint(e.target.value);
});
document.getElementById("tagFormCancel").addEventListener("click", closeTagForm);
document.getElementById("tagFormSave").addEventListener("click", async () => {
  const category = document.getElementById("tagCategorySelect").value;
  const value = document.getElementById("tagValueInput").value.trim();
  if (!value) return;
  const body = { category, value };
  if (tagFormPendingBox) {
    body.bbox_x = tagFormPendingBox.x;
    body.bbox_y = tagFormPendingBox.y;
    body.bbox_w = tagFormPendingBox.w;
    body.bbox_h = tagFormPendingBox.h;
  }
  let res;
  if (tagFormMode === "edit") {
    res = await authFetch(`/api/tags/${tagFormEditingId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } else {
    body.photo_path = allImages[currentLightboxIndex];
    res = await authFetch("/api/tags", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }
  if (!res.ok) return;
  logEvent("tag_saved", `${category}:${value}`);
  closeTagForm();
  await loadTagsForCurrentPhoto();
});
document.getElementById("tagFormDelete").addEventListener("click", async () => {
  if (!tagFormEditingId) return;
  const res = await authFetch(`/api/tags/${tagFormEditingId}`, { method: "DELETE" });
  if (!res.ok) return;
  logEvent("tag_deleted", String(tagFormEditingId));
  closeTagForm();
  await loadTagsForCurrentPhoto();
});

// ---- "More actions" menu - download/select-mode moved here 2026-08-05,
// no longer needed front-and-center now that tagging is the main workflow ----

document.getElementById("moreActionsBtn").addEventListener("click", (e) => {
  e.stopPropagation();
  const menu = document.getElementById("moreActionsMenu");
  const opening = menu.classList.contains("hidden");
  menu.classList.toggle("hidden", !opening);
  document.getElementById("moreActionsBtn").setAttribute("aria-expanded", String(opening));
});
document.addEventListener("click", (e) => {
  const wrap = document.getElementById("moreActionsWrap");
  if (wrap && !wrap.contains(e.target)) {
    document.getElementById("moreActionsMenu").classList.add("hidden");
    document.getElementById("moreActionsBtn").setAttribute("aria-expanded", "false");
  }
});
document.getElementById("selectModeBtn").addEventListener("click", () => {
  document.getElementById("moreActionsMenu").classList.add("hidden");
});
document.getElementById("downloadAllBtn").addEventListener("click", () => {
  document.getElementById("moreActionsMenu").classList.add("hidden");
});

// ---- Admin-only photo source setting - hidden entirely for a member
// (403 on the GET below just leaves settingsBtn hidden, no error shown) ----

async function initPhotosSourceSetting() {
  const res = await authFetch("/api/settings/photos-source");
  if (!res.ok) return;
  document.getElementById("settingsBtn").classList.remove("hidden");
}

document.getElementById("settingsBtn").addEventListener("click", async () => {
  document.getElementById("moreActionsMenu").classList.add("hidden");
  const res = await authFetch("/api/settings/photos-source");
  if (!res.ok) return;
  const { active, available } = await res.json();
  const select = document.getElementById("photosSourceSelect");
  select.innerHTML = "";
  for (const name of available) {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    select.appendChild(opt);
  }
  select.value = active;
  document.getElementById("settingsModal").classList.remove("hidden");
});
document.getElementById("settingsModalCancel").addEventListener("click", () => {
  document.getElementById("settingsModal").classList.add("hidden");
});
document.getElementById("settingsModalSave").addEventListener("click", async () => {
  const active = document.getElementById("photosSourceSelect").value;
  const res = await authFetch("/api/settings/photos-source", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ active }),
  });
  if (!res.ok) return;
  document.getElementById("settingsModal").classList.add("hidden");
  logEvent("photos_source_changed", active);
  await loadTree();
});

// ---- Help / photo-info icon buttons on the lightbox ----

document.getElementById("lbHelpBtn").addEventListener("click", () => {
  document.getElementById("helpBtn").click();
});
document.getElementById("lbInfoBtn").addEventListener("click", () => {
  const path = allImages[currentLightboxIndex];
  document.getElementById("photoInfoFilename").textContent = path.split("/").pop();
  const list = document.getElementById("photoInfoTagList");
  list.innerHTML = "";
  if (currentPhotoTags.length === 0) {
    const p = document.createElement("p");
    p.textContent = "Inga taggar än.";
    list.appendChild(p);
  } else {
    for (const tag of currentPhotoTags) {
      const row = document.createElement("p");
      const region = tag.bbox ? " (markerat område)" : "";
      row.textContent = `${TAG_CATEGORY_LABELS[tag.category] || tag.category}: ${tag.value}${region}`;
      list.appendChild(row);
    }
  }
  document.getElementById("photoInfoModal").classList.remove("hidden");
});
document.getElementById("photoInfoModalClose").addEventListener("click", () => {
  document.getElementById("photoInfoModal").classList.add("hidden");
});

// ---- Manual bounding-box drawing: an explicit tool (armed via
// #lbDrawBoxBtn), not an always-on drag. Two reasons: it's what Joakim
// asked for directly (2026-08-05, "I would prefer a drag a square-tool"),
// and an always-on drag would hijack ordinary scrolling/pinch gestures on
// a touch device every time a finger touched the photo. After the initial
// drag, the box stays adjustable (drag its body to move, its corners to
// resize) before committing to the tag-details form - added same day
// after live use found two real problems: a too-small drag silently did
// nothing ("didn't stick", no feedback at all), and drawing an exact box
// around a face by hand is genuinely hard on the first attempt.

let drawPhase = "idle"; // "idle" | "armed" | "adjusting"
let drawBox = null; // {x,y,w,h} fractions, while armed/adjusting
let dragMode = null; // "new" | "move" | "resize", while a pointer is down
let dragAnchor = null; // meaning depends on dragMode

const lbImageWrap = document.getElementById("lbImageWrap");
const lbDrawingBoxEl = document.getElementById("lbDrawingBox");
const lbDrawBoxBtn = document.getElementById("lbDrawBoxBtn");

for (const corner of ["nw", "ne", "sw", "se"]) {
  const handle = document.createElement("div");
  handle.className = `lb-box-handle lb-box-handle-${corner}`;
  handle.dataset.corner = corner;
  lbDrawingBoxEl.appendChild(handle);
}

function renderDrawBox() {
  if (!drawBox) {
    lbDrawingBoxEl.classList.add("hidden");
    return;
  }
  lbDrawingBoxEl.style.left = drawBox.x * 100 + "%";
  lbDrawingBoxEl.style.top = drawBox.y * 100 + "%";
  lbDrawingBoxEl.style.width = drawBox.w * 100 + "%";
  lbDrawingBoxEl.style.height = drawBox.h * 100 + "%";
  lbDrawingBoxEl.classList.remove("hidden");
  lbDrawingBoxEl.classList.toggle("adjusting", drawPhase === "adjusting");
}

function setDrawPhase(phase) {
  drawPhase = phase;
  lbImageWrap.classList.toggle("drawing-active", phase !== "idle");
  if (phase === "idle") {
    lbDrawBoxBtn.textContent = "▭ Rita ruta";
    lbDrawBoxBtn.setAttribute("aria-pressed", "false");
    lbDrawBoxBtn.classList.remove("armed");
  } else if (phase === "armed") {
    lbDrawBoxBtn.textContent = "✕ Avbryt ritning";
    lbDrawBoxBtn.setAttribute("aria-pressed", "true");
    lbDrawBoxBtn.classList.add("armed");
  } else {
    lbDrawBoxBtn.textContent = "✓ Klar med ruta";
    lbDrawBoxBtn.setAttribute("aria-pressed", "true");
    lbDrawBoxBtn.classList.add("armed");
  }
}

function disarmDrawBox() {
  setDrawPhase("idle");
  drawBox = null;
  dragMode = null;
  dragAnchor = null;
  renderDrawBox();
}

lbDrawBoxBtn.addEventListener("click", () => {
  if (drawPhase === "idle") {
    setDrawPhase("armed");
  } else if (drawPhase === "armed") {
    disarmDrawBox();
  } else {
    const box = drawBox;
    disarmDrawBox();
    openTagForm({ mode: "create", pendingBox: box });
  }
});

function pointFromEvent(e) {
  const rect = lbImageWrap.getBoundingClientRect();
  const point = e.touches && e.touches.length ? e.touches[0] : e;
  return {
    x: clamp01((point.clientX - rect.left) / rect.width),
    y: clamp01((point.clientY - rect.top) / rect.height),
  };
}

function boxFromCorners(a, b) {
  return { x: Math.min(a.x, b.x), y: Math.min(a.y, b.y), w: Math.abs(a.x - b.x), h: Math.abs(a.y - b.y) };
}

// Judged in real screen pixels, not a fraction of the image - a
// fraction-based cutoff (the original design) silently swallowed
// small-but-deliberate face-sized boxes on a large photo.
const MIN_DRAG_PX = 6;

function startPointer(e) {
  const handleEl = e.target.closest && e.target.closest(".lb-box-handle");
  if (handleEl) {
    dragMode = "resize";
    dragAnchor = { corner: handleEl.dataset.corner };
    e.preventDefault();
    return;
  }
  if (drawPhase === "adjusting" && e.target.closest && e.target.closest("#lbDrawingBox")) {
    const p = pointFromEvent(e);
    dragMode = "move";
    dragAnchor = { startX: p.x, startY: p.y, boxStart: { ...drawBox } };
    e.preventDefault();
    return;
  }
  if (drawPhase === "idle") return;
  // armed (no box yet), or adjusting but clicked outside the current box:
  // start a fresh box, discarding whatever was there before.
  const p = pointFromEvent(e);
  dragMode = "new";
  dragAnchor = { start: p };
  drawBox = { x: p.x, y: p.y, w: 0, h: 0 };
  renderDrawBox();
  e.preventDefault();
}

function movePointer(e) {
  if (!dragMode) return;
  e.preventDefault();
  const p = pointFromEvent(e);
  if (dragMode === "new") {
    drawBox = boxFromCorners(dragAnchor.start, p);
  } else if (dragMode === "move") {
    const dx = p.x - dragAnchor.startX;
    const dy = p.y - dragAnchor.startY;
    const w = dragAnchor.boxStart.w;
    const h = dragAnchor.boxStart.h;
    drawBox = {
      x: clamp01(Math.min(Math.max(dragAnchor.boxStart.x + dx, 0), 1 - w)),
      y: clamp01(Math.min(Math.max(dragAnchor.boxStart.y + dy, 0), 1 - h)),
      w,
      h,
    };
  } else if (dragMode === "resize") {
    // The corner opposite the one being dragged stays fixed in place.
    const fixed = {
      x: dragAnchor.corner.includes("e") ? drawBox.x : drawBox.x + drawBox.w,
      y: dragAnchor.corner.includes("s") ? drawBox.y : drawBox.y + drawBox.h,
    };
    drawBox = boxFromCorners(fixed, p);
  }
  renderDrawBox();
}

function endPointer() {
  if (!dragMode) return;
  const wasNew = dragMode === "new";
  dragMode = null;
  dragAnchor = null;
  if (!drawBox) return;
  const rect = lbImageWrap.getBoundingClientRect();
  const pxW = drawBox.w * rect.width;
  const pxH = drawBox.h * rect.height;
  if (wasNew && (pxW < MIN_DRAG_PX || pxH < MIN_DRAG_PX)) {
    // Too small to have been a deliberate box - stay armed and let the
    // user try again, rather than silently discarding the whole attempt
    // with no feedback (the original design's actual reported failure).
    drawBox = null;
    renderDrawBox();
    return;
  }
  setDrawPhase("adjusting");
  renderDrawBox();
}

lbImageWrap.addEventListener("mousedown", startPointer);
document.addEventListener("mousemove", movePointer);
document.addEventListener("mouseup", endPointer);
lbImageWrap.addEventListener("touchstart", startPointer, { passive: false });
document.addEventListener("touchmove", movePointer, { passive: false });
document.addEventListener("touchend", endPointer);
document.addEventListener("touchcancel", endPointer);

async function loadTree() {
  const res = await authFetch("/api/tree");
  const sections = await res.json();
  renderTree(sections);
}

document.getElementById("downloadFolderLabel").addEventListener("click", () => {
  pickDownloadFolder();
});

(async function init() {
  await tryRestoreDownloadFolder();
  enterGallery();
  initPhotosSourceSetting();
})();
