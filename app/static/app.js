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
  if (downloadDirHandle) {
    const res = await fetch(`/original?p=${encodeURIComponent(relpath)}`);
    if (!res.ok) throw new Error("download failed: " + relpath);
    const blob = await res.blob();
    const filename = relpath.split("/").pop();
    const fileHandle = await uniqueFileHandle(downloadDirHandle, filename);
    const writable = await fileHandle.createWritable();
    await writable.write(blob);
    await writable.close();
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

async function downloadAsZip(paths, btn) {
  const original = btn.textContent;
  const originalBg = btn.style.background;
  btn.disabled = true;
  setBtnProgress(btn, 0, `Bygger ZIP (${paths.length} bilder)...`);
  downloadsInProgress++;
  try {
    const res = await fetch("/api/zip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paths }),
    });
    if (!res.ok) throw new Error("zip failed");
    const filename = "mammas_bilder.zip";
    const total = parseInt(res.headers.get("Content-Length") || "0", 10);

    let writable = null;
    const chunks = [];
    if (downloadDirHandle) {
      const fileHandle = await uniqueFileHandle(downloadDirHandle, filename);
      writable = await fileHandle.createWritable();
    }

    const reader = res.body.getReader();
    let received = 0;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      received += value.length;
      if (writable) {
        await writable.write(value);
      } else {
        chunks.push(value);
      }
      const pct = total ? Math.round((received / total) * 100) : null;
      setBtnProgress(
        btn,
        pct,
        pct != null
          ? `Sparar... ${pct}% (${(received / 1e6).toFixed(0)} MB)`
          : `Sparar... ${(received / 1e6).toFixed(0)} MB`
      );
    }

    if (writable) {
      await writable.close();
    } else {
      const blob = new Blob(chunks);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    }
    setBtnProgress(btn, 100, "Klart!");
  } catch (e) {
    setBtnProgress(btn, null, "Fel vid nedladdning");
  } finally {
    downloadsInProgress--;
  }
  setTimeout(() => {
    btn.style.background = originalBg;
    btn.textContent = original;
    btn.disabled = false;
  }, 3000);
}

async function setupDownloadFolder() {
  const setupError = document.getElementById("setupError");
  try {
    const handle = await window.showDirectoryPicker({ mode: "readwrite" });
    await idbSet("dir", handle);
    downloadDirHandle = handle;
    logEvent("folder_picked", handle.name || "");
    enterGallery();
  } catch (e) {
    if (e.name !== "AbortError") {
      setupError.textContent = "Kunde inte välja mapp: " + e.message;
    }
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
  document.getElementById("setup").classList.add("hidden");
  document.getElementById("gallery").classList.remove("hidden");
  document.getElementById("downloadFolderLabel").textContent = downloadDirHandle
    ? "Bilder sparas i: " + (downloadDirHandle.name || "vald mapp")
    : "Nedladdningar sparas enligt webbläsarens nedladdningsinställning";
  loadTree();
}

let selectMode = false;
const marked = new Set();
let allImages = [];
let currentLightboxIndex = -1;

function loadSet(key) {
  try {
    return new Set(JSON.parse(localStorage.getItem(key) || "[]"));
  } catch (e) {
    return new Set();
  }
}
function saveSet(key, set) {
  localStorage.setItem(key, JSON.stringify(Array.from(set)));
}

const visitedHeadlines = loadSet("mpv_visited_headlines");
const collapsedHeadlines = loadSet("mpv_collapsed_headlines");
let headlineCount = 0;

function toggleVisited(headline) {
  if (visitedHeadlines.has(headline)) {
    visitedHeadlines.delete(headline);
  } else {
    visitedHeadlines.add(headline);
  }
  saveSet("mpv_visited_headlines", visitedHeadlines);
  updateVisitedUI();
  logEvent("album_visited_toggle", headline + ":" + visitedHeadlines.has(headline));
}

function updateVisitedUI() {
  document.getElementById("visitedCounter").textContent =
    `${visitedHeadlines.size} av ${headlineCount} album visade`;
  document.querySelectorAll(".nav-pill").forEach((pill) => {
    pill.classList.toggle("visited", visitedHeadlines.has(pill.dataset.headline));
  });
}

function renderTree(sections) {
  const tree = document.getElementById("tree");
  const nav = document.getElementById("albumNav");
  tree.innerHTML = "";
  nav.innerHTML = "";
  allImages = [];
  headlineCount = sections.length;

  for (const section of sections) {
    const album = document.createElement("div");
    album.className = "album";
    album.dataset.headline = section.headline;

    const row = document.createElement("div");
    row.className = "headline-row";
    const h = document.createElement("h2");
    h.className = "headline";
    h.textContent = section.headline;
    const visitedBtn = document.createElement("button");
    visitedBtn.className = "visited-btn";
    const setVisitedBtnLabel = () => {
      const done = visitedHeadlines.has(section.headline);
      visitedBtn.textContent = done ? "✓ Klar" : "Markera som klar";
      visitedBtn.classList.toggle("done", done);
    };
    setVisitedBtnLabel();
    visitedBtn.addEventListener("click", () => {
      toggleVisited(section.headline);
      setVisitedBtnLabel();
    });

    const collapseBtn = document.createElement("button");
    collapseBtn.className = "collapse-btn";
    const isCollapsed = collapsedHeadlines.has(section.headline);
    collapseBtn.textContent = isCollapsed ? "Visa" : "Dölj";
    const actions = document.createElement("div");
    actions.className = "headline-actions";
    actions.appendChild(visitedBtn);
    actions.appendChild(collapseBtn);
    row.appendChild(h);
    row.appendChild(actions);
    album.appendChild(row);

    const body = document.createElement("div");
    body.className = "album-body" + (isCollapsed ? " collapsed" : "");

    collapseBtn.addEventListener("click", () => {
      const nowCollapsed = body.classList.toggle("collapsed");
      collapseBtn.textContent = nowCollapsed ? "Visa" : "Dölj";
      if (nowCollapsed) collapsedHeadlines.add(section.headline);
      else collapsedHeadlines.delete(section.headline);
      saveSet("mpv_collapsed_headlines", collapsedHeadlines);
    });

    for (const chunk of section.chunks) {
      const ct = document.createElement("div");
      ct.className = "chunk-title";
      ct.textContent = chunk.path;
      body.appendChild(ct);
      const grid = document.createElement("div");
      grid.className = "grid";
      for (const img of chunk.images) {
        const idx = allImages.length;
        allImages.push(img);
        const thumb = document.createElement("div");
        thumb.className = "thumb";
        thumb.dataset.path = img;
        thumb.dataset.idx = idx;
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

    const pill = document.createElement("button");
    pill.className = "nav-pill" + (visitedHeadlines.has(section.headline) ? " visited" : "");
    pill.dataset.headline = section.headline;
    pill.textContent = section.headline;
    pill.addEventListener("click", () => {
      album.scrollIntoView({ behavior: "smooth", block: "start" });
      logEvent("nav_jump", section.headline);
    });
    nav.appendChild(pill);
  }
  updateVisitedUI();
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
  logEvent("download_all_zip", `count=${allImages.length}`);
  downloadAsZip(allImages, document.getElementById("downloadAllBtn"));
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
  logEvent("download_selected_zip", `count=${paths.length}`);
  await downloadAsZip(paths, document.getElementById("downloadSelectedBtn"));
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
    await fetch("/api/voiceover", { method: "POST", body: form });
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

document.getElementById("voiceoverRecordBtn").addEventListener("click", startVoiceover);
document.getElementById("voiceoverStopBtn").addEventListener("click", stopVoiceover);

async function openVoiceoverList() {
  const modal = document.getElementById("voiceoverListModal");
  const container = document.getElementById("voiceoverListItems");
  container.textContent = "Laddar...";
  modal.classList.remove("hidden");
  const res = await fetch("/api/voiceovers");
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
    label.textContent = `${date.toLocaleString("sv-SE")} — ${item.image_count} bilder`;
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
  const res = await fetch(`/api/voiceover/${id}`);
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
}
function closeLightbox() {
  document.getElementById("lightbox").classList.add("hidden");
}
function lightboxStep(delta) {
  currentLightboxIndex = (currentLightboxIndex + delta + allImages.length) % allImages.length;
  document.getElementById("lbImg").src = `/original?p=${encodeURIComponent(allImages[currentLightboxIndex])}`;
  logEvent("image_view", allImages[currentLightboxIndex]);
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
  if (document.getElementById("lightbox").classList.contains("hidden")) return;
  if (e.key === "Escape") closeLightbox();
  else if (e.altKey && e.key === "ArrowLeft") {
    e.preventDefault();
    closeLightbox();
  } else if (e.key === "ArrowLeft") lightboxStep(-1);
  else if (e.key === "ArrowRight") lightboxStep(1);
});

async function loadTree() {
  const res = await fetch("/api/tree");
  const sections = await res.json();
  renderTree(sections);
}

document.getElementById("pickFolderBtn").addEventListener("click", setupDownloadFolder);
document.getElementById("skipFolderBtn").addEventListener("click", () => {
  downloadDirHandle = null;
  logEvent("folder_skipped");
  enterGallery();
});

function checkCompatibility() {
  if (typeof window.showDirectoryPicker === "function") {
    document.getElementById("pickFolderBtn").classList.remove("hidden");
    return;
  }
  document.getElementById("pickFolderBtn").classList.add("hidden");
  const setupError = document.getElementById("setupError");
  if (!window.isSecureContext) {
    setupError.textContent =
      "Sidan är inte öppnad över https://. Kontrollera att adressen i webbläsaren " +
      "börjar med https:// (inte http://). Adress just nu: " + location.href;
  } else {
    setupError.textContent =
      "Den här webbläsaren stöder inte mappval (Microsoft Edge eller Google Chrome " +
      "behövs för det) - men du kan fortsätta ändå, nedladdningar sparas då enligt " +
      "webbläsarens vanliga nedladdningsinställning.";
  }
}

(async function init() {
  checkCompatibility();
  if (await tryRestoreDownloadFolder()) {
    enterGallery();
  }
})();
