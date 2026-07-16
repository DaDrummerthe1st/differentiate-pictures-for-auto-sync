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

async function saveImageToFolder(relpath) {
  const res = await fetch(`/original?p=${encodeURIComponent(relpath)}`);
  if (!res.ok) throw new Error("download failed: " + relpath);
  const blob = await res.blob();
  const filename = relpath.split("/").pop();
  const fileHandle = await uniqueFileHandle(downloadDirHandle, filename);
  const writable = await fileHandle.createWritable();
  await writable.write(blob);
  await writable.close();
}

function showProgress(text) {
  const el = document.getElementById("progress");
  el.textContent = text;
  el.classList.remove("hidden");
}
function hideProgress() {
  document.getElementById("progress").classList.add("hidden");
}

async function setupDownloadFolder() {
  const setupError = document.getElementById("setupError");
  try {
    const handle = await window.showDirectoryPicker({ mode: "readwrite" });
    await idbSet("dir", handle);
    downloadDirHandle = handle;
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
  await primeUsedNames();
  document.getElementById("setup").classList.add("hidden");
  document.getElementById("gallery").classList.remove("hidden");
  document.getElementById("downloadFolderLabel").textContent =
    "Bilder sparas i: " + (downloadDirHandle.name || "vald mapp");
  loadTree();
}

let selectMode = false;
const marked = new Set();
let allImages = [];
let currentLightboxIndex = -1;

function renderTree(sections) {
  const tree = document.getElementById("tree");
  tree.innerHTML = "";
  allImages = [];
  for (const section of sections) {
    const h = document.createElement("div");
    h.className = "headline";
    h.textContent = section.headline;
    tree.appendChild(h);
    for (const chunk of section.chunks) {
      const ct = document.createElement("div");
      ct.className = "chunk-title";
      ct.textContent = chunk.path;
      tree.appendChild(ct);
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
      tree.appendChild(grid);
    }
  }
}

function onThumbClick(thumbEl) {
  const path = thumbEl.dataset.path;
  if (selectMode) {
    if (marked.has(path)) {
      marked.delete(path);
      thumbEl.classList.remove("marked");
    } else {
      marked.add(path);
      thumbEl.classList.add("marked");
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

document.getElementById("selectModeBtn").addEventListener("click", () => {
  selectMode = !selectMode;
  const btn = document.getElementById("selectModeBtn");
  btn.classList.toggle("active", selectMode);
  btn.textContent = selectMode ? "Markeringsläge PÅ" : "Markera bilder";
  if (!selectMode) {
    marked.clear();
    document.querySelectorAll(".thumb.marked").forEach((el) => el.classList.remove("marked"));
    updateDownloadSelectedBtn();
  }
});

document.getElementById("downloadSelectedBtn").addEventListener("click", async () => {
  const paths = Array.from(marked);
  let done = 0;
  showProgress(`Sparar ${done}/${paths.length}...`);
  for (const p of paths) {
    await saveImageToFolder(p);
    done++;
    showProgress(`Sparar ${done}/${paths.length}...`);
  }
  hideProgress();
  marked.clear();
  document.querySelectorAll(".thumb.marked").forEach((el) => el.classList.remove("marked"));
  updateDownloadSelectedBtn();
});

function openLightbox(idx) {
  currentLightboxIndex = idx;
  const lb = document.getElementById("lightbox");
  document.getElementById("lbImg").src = `/original?p=${encodeURIComponent(allImages[idx])}`;
  lb.classList.remove("hidden");
}
function closeLightbox() {
  document.getElementById("lightbox").classList.add("hidden");
}
function lightboxStep(delta) {
  currentLightboxIndex = (currentLightboxIndex + delta + allImages.length) % allImages.length;
  document.getElementById("lbImg").src = `/original?p=${encodeURIComponent(allImages[currentLightboxIndex])}`;
}

document.getElementById("lbClose").addEventListener("click", closeLightbox);
document.getElementById("lbPrev").addEventListener("click", () => lightboxStep(-1));
document.getElementById("lbNext").addEventListener("click", () => lightboxStep(1));
document.getElementById("lbDownload").addEventListener("click", async (e) => {
  const btn = e.currentTarget;
  const original = btn.textContent;
  btn.textContent = "Sparar...";
  try {
    await saveImageToFolder(allImages[currentLightboxIndex]);
    btn.textContent = "Sparad!";
  } catch (err) {
    btn.textContent = "Fel!";
  }
  setTimeout(() => (btn.textContent = original), 1200);
});
document.addEventListener("keydown", (e) => {
  if (document.getElementById("lightbox").classList.contains("hidden")) return;
  if (e.key === "Escape") closeLightbox();
  if (e.key === "ArrowLeft") lightboxStep(-1);
  if (e.key === "ArrowRight") lightboxStep(1);
});

async function loadTree() {
  const res = await fetch("/api/tree");
  const sections = await res.json();
  renderTree(sections);
}

document.getElementById("pickFolderBtn").addEventListener("click", setupDownloadFolder);

(async function init() {
  if (await tryRestoreDownloadFolder()) {
    enterGallery();
  }
})();
