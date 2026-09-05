// Endast klientsidan. Allt här är en fejkad databas i minnet som riktiga
// klick faktiskt förändrar — ingen server, inget lämnar den här sidan. Se
// documentation/upload-and-share/ för designen detta illustrerar.

function icon(name) { return `<span class="material-symbols-outlined">${name}</span>`; }
function termsLabel(terms) { return terms === "free" ? "Fri" : "Strikt"; }
function termsIcon(terms) { return terms === "free" ? "public" : "lock"; }
// Batch names are user-typed (Upload tab / guest upload) and become tag
// text rendered via innerHTML below — escape before interpolating so a
// batch name like "<img onerror=...>" can't run as markup.
function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// ---------------------------------------------------------------- seed data

const DB = {
  users: {
    u1: { id: "u1", name: "Joakim", username: "joakim", email: "joakim.reuterborg@gmail.com" },
    u2: { id: "u2", name: "Elisabeth", username: "elisabeth", email: "elisabeth.reuterborg@gmail.com" },
    ev1acct: { id: "ev1acct", name: "Anna & Eriks bröllop (eventkonto)", username: "event-annaerik", email: null, isEventAccount: true },
  },
  photos: [],
  events: [
    { id: "ev1", name: "Anna & Eriks bröllop", hostUserId: "u1", accountId: "ev1acct",
      axes: { uploadAccess: "free-for-all", visibility: "all", tv: true } },
  ],
};

let nextUserSeq = 3;
let nextShareSeq = 1;
let nextPhotoSeq = 1;

function mkPhoto(filename, batch, ownerId, tags, opts) {
  opts = opts || {};
  const id = "p" + nextPhotoSeq++;
  return {
    id, filename, batch, ownerId,
    tags: tags.map((t) => ({ text: t.text, by: t.by, endorsedBy: [] })),
    shares: opts.shares || [],
    isEventPhoto: !!opts.isEventPhoto,
    curated: !!opts.curated,
  };
}

DB.photos.push(
  mkPhoto("beach1.jpg", "Sommaren 2019", "u1", [{ text: "Sommaren 2019", by: "u1" }, { text: "Strand", by: "u1" }], {
    shares: [{ id: "s" + nextShareSeq++, kind: "username", toUserId: "u2", terms: "strict", status: "active", sharedByUserId: "u1" }],
  }),
  mkPhoto("cake.jpg", "Sommaren 2019", "u1", [{ text: "Sommaren 2019", by: "u1" }, { text: "Kalas", by: "u1" }]),
  mkPhoto("mountain.jpg", "Vandringstur", "u2", [{ text: "Vandringstur", by: "u2" }], {
    shares: [{ id: "s" + nextShareSeq++, kind: "username", toUserId: "u1", terms: "free", status: "active", sharedByUserId: "u2" }],
  }),
  mkPhoto("loki.jpg", "Vandringstur", "u2", [{ text: "Vandringstur", by: "u2" }, { text: "Loki", by: "u2" }], {
    shares: [{ id: "s" + nextShareSeq++, kind: "username", toUserId: "u1", terms: "strict", status: "active", sharedByUserId: "u2" }],
  }),
  mkPhoto("sunset.jpg", "web-upload-elisabeth-20260601", "u2", [{ text: "web-upload-elisabeth-20260601", by: "u2" }], {
    shares: [{ id: "s" + nextShareSeq++, kind: "email", toEmail: "anna.friend@example.com", terms: "free", status: "pending_signup", sharedByUserId: "u2" }],
  }),
  mkPhoto("christmas.jpg", "Jul 2025", "u1", [{ text: "Jul 2025", by: "u1" }, { text: "Barnen", by: "u1" }], {
    shares: [{ id: "s" + nextShareSeq++, kind: "platform", toUserId: null, toEmail: null, terms: "free", status: "link_open_pending", token: "tok_9f2a", sharedByUserId: "u1" }],
  }),
  mkPhoto("snow.jpg", "Jul 2025", "u1", [{ text: "Jul 2025", by: "u1" }]),
  mkPhoto("puppy2.jpg", "Vandringstur", "u2", [{ text: "Vandringstur", by: "u2" }, { text: "Loki igen", by: "u2" }])
);

const EVENT_TAG = "Anna & Eriks bröllop";
[
  ["ceremony1.jpg", true], ["ceremony2.jpg", false], ["firstdance.jpg", true],
  ["cake-cutting.jpg", false], ["guests-dancing.jpg", true], ["blurry-hallway.jpg", false],
].forEach(([fn, curated]) => {
  DB.photos.push(mkPhoto(fn, EVENT_TAG, "ev1acct", [{ text: EVENT_TAG, by: "ev1acct" }], { isEventPhoto: true, curated }));
});

const STOCK_POOL = [
  { filename: "IMG_2044.jpg", emoji: "🌻" }, { filename: "IMG_2051.jpg", emoji: "🚗" },
  { filename: "IMG_2077.jpg", emoji: "🍕" }, { filename: "IMG_2101.jpg", emoji: "🎸" },
  { filename: "IMG_2140.jpg", emoji: "🏕️" }, { filename: "IMG_2188.jpg", emoji: "🌅" },
  { filename: "IMG_2203.jpg", emoji: "🍂" }, { filename: "IMG_2255.jpg", emoji: "🎉" },
  { filename: "IMG_2301.jpg", emoji: "🐶" }, { filename: "IMG_2340.jpg", emoji: "🏔️" },
].map((f, i) => ({ ...f, poolId: "stock" + i }));

const EMOJI_FALLBACK = { "beach1.jpg": "🏖️", "cake.jpg": "🎂", "mountain.jpg": "🏔️", "loki.jpg": "🐶",
  "sunset.jpg": "🌅", "christmas.jpg": "🎄", "snow.jpg": "❄️", "puppy2.jpg": "🐶",
  "ceremony1.jpg": "💍", "ceremony2.jpg": "💒", "firstdance.jpg": "💃", "cake-cutting.jpg": "🎂",
  "guests-dancing.jpg": "🕺", "blurry-hallway.jpg": "🚪" };
const COLORS = ["#3a5a7a", "#5a3a6a", "#3a6a4a", "#6a4a2a", "#2a4a6a", "#6a2a4a", "#4a6a2a", "#2a5a5a"];
function colorFor(id) {
  let h = 0;
  for (const c of id) h += c.charCodeAt(0);
  return COLORS[h % COLORS.length];
}
function emojiFor(photo) { return EMOJI_FALLBACK[photo.filename] || "🖼️"; }

// -------------------------------------------------------------------- state

let currentUserId = "u1";
let currentTab = "gallery";
let selectedPool = new Set();
let pool = STOCK_POOL.slice();
let openPhotoId = null;

function me() { return DB.users[currentUserId]; }
function userName(id) { return DB.users[id] ? DB.users[id].name : "(okänd)"; }

// ------------------------------------------------------------ permissions

function activeShareFor(photo, userId) {
  return photo.shares.find((s) => s.toUserId === userId && s.status === "active");
}
function isVisibleTo(photo, userId) {
  return photo.ownerId === userId || !!activeShareFor(photo, userId);
}
function canDownload(photo, userId) {
  if (photo.ownerId === userId) return true;
  const s = activeShareFor(photo, userId);
  return !!s && s.terms === "free";
}
function canManageSharing(photo, userId) {
  if (photo.ownerId === userId) return true;
  const s = activeShareFor(photo, userId);
  return !!s && s.terms === "free";
}

// ---------------------------------------------------------------- toasts

let toastTimer = null;
function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.add("hidden"), 3200);
}

// ------------------------------------------------------------------ tabs

function switchTab(name) {
  currentTab = name;
  document.querySelectorAll("#tabNav .nav-pill").forEach((b) => b.classList.toggle("current", b.dataset.tab === name));
  document.querySelectorAll(".tab-panel").forEach((p) => p.classList.toggle("hidden", p.id !== "tab-" + name));
  render();
}

function switchUser(id) {
  currentUserId = id;
  render();
}

// -------------------------------------------------------------- gallery

function thumbHtml(photo, opts) {
  opts = opts || {};
  let chip = "";
  if (photo.ownerId === currentUserId) chip = `<span class="chip owner">${icon("person")}Din</span>`;
  else {
    const s = activeShareFor(photo, currentUserId);
    if (s) chip = `<span class="chip ${s.terms}">${icon(termsIcon(s.terms))}${termsLabel(s.terms)}</span>`;
  }
  if (opts.curatedChip && photo.curated) chip += `<span class="chip curated" style="right:auto;left:0.4rem;">${icon("star")}Kurerad</span>`;
  return `<div class="thumb ${photo.curated && opts.curatedChip ? "curated" : ""}" style="background:${colorFor(photo.id)}" onclick="openPhotoDetail('${photo.id}')">
    <span class="emoji">${emojiFor(photo)}</span>
    ${chip}
    <span class="fname">${photo.filename}</span>
  </div>`;
}

function render() {
  renderUserSwitch();
  updatePendingBadge();
  if (currentTab === "gallery") renderGallery();
  if (currentTab === "upload") renderUpload();
  if (currentTab === "sharing") renderSharing();
  if (currentTab === "events") renderEvents();
  if (openPhotoId) renderPhotoDetail(openPhotoId);
}

function renderUserSwitch() {
  const sel = document.getElementById("userSwitch");
  const people = Object.values(DB.users).filter((u) => !u.isEventAccount);
  sel.innerHTML = people.map((u) => `<option value="${u.id}" ${u.id === currentUserId ? "selected" : ""}>${u.name}</option>`).join("");
}

function renderGallery() {
  const mine = DB.photos.filter((p) => !p.isEventPhoto && isVisibleTo(p, currentUserId));
  document.getElementById("galleryGrid").innerHTML = mine.map((p) => thumbHtml(p)).join("");
  document.getElementById("galleryEmptyHint").textContent = mine.length
    ? ""
    : "Inga bilder än för " + me().name + " — ladda upp några, eller ta emot en delning.";
}

// --------------------------------------------------------------- upload

function renderUpload() {
  document.getElementById("batchDefaultHint").textContent =
    "Tomt namn → katalog = web-upload-" + me().username + "-{tidsstämpel}";
  const poolEl = document.getElementById("filePool");
  if (!pool.length) {
    poolEl.innerHTML = '<p class="empty-note">Inga fler exempelbilder den här sessionen — ladda om sidan för att återställa.</p>';
  } else {
    poolEl.innerHTML = pool.map((f) =>
      `<div class="pool-item ${selectedPool.has(f.poolId) ? "selected" : ""}" style="background:${colorFor(f.poolId)}" onclick="togglePoolItem('${f.poolId}')" title="${f.filename}">${f.emoji}</div>`
    ).join("");
  }
  document.getElementById("selectedCount").textContent = selectedPool.size;
  document.getElementById("uploadBtn").disabled = selectedPool.size === 0;
}

function togglePoolItem(poolId) {
  if (selectedPool.has(poolId)) selectedPool.delete(poolId);
  else selectedPool.add(poolId);
  renderUpload();
}

function doUpload() {
  const typed = document.getElementById("batchName").value.trim();
  const batch = typed || `web-upload-${me().username}-${Date.now()}`;
  const chosen = pool.filter((f) => selectedPool.has(f.poolId));
  chosen.forEach((f) => {
    DB.photos.push(mkPhoto(f.filename, batch, currentUserId, [{ text: batch, by: currentUserId }]));
  });
  pool = pool.filter((f) => !selectedPool.has(f.poolId));
  const count = chosen.length;
  selectedPool.clear();
  document.getElementById("batchName").value = "";
  toast(`Laddade upp ${count} bild${count === 1 ? "" : "er"} som "${batch}"`);
  switchTab("gallery");
}

// -------------------------------------------------------------- sharing

function renderSharing() {
  const incoming = [];
  const outgoing = [];
  const sharedByMe = [];
  DB.photos.forEach((p) => {
    p.shares.forEach((s) => {
      if (s.toUserId === currentUserId && s.status === "pending_accept") incoming.push([p, s]);
      if (s.sharedByUserId === currentUserId && s.status === "pending_signup") outgoing.push([p, s]);
      if (s.sharedByUserId === currentUserId && s.status === "link_open_pending") outgoing.push([p, s]);
      if (s.sharedByUserId === currentUserId && s.status === "active") sharedByMe.push([p, s]);
    });
  });

  document.getElementById("incomingList").innerHTML = incoming.length ? incoming.map(([p, s]) =>
    `<li><div class="li-main"><span style="font-size:1.4rem;">${emojiFor(p)}</span><div>${p.filename}<div class="muted">från ${userName(s.sharedByUserId)} · ${icon(termsIcon(s.terms))}${termsLabel(s.terms)} · via delningslänk</div></div></div>
     <div class="li-actions"><button class="btn small good" onclick="acceptIncoming('${p.id}','${s.id}')">${icon("check")}Acceptera</button><button class="btn small ghost" onclick="declineIncoming('${p.id}','${s.id}')">${icon("close")}Neka</button></div></li>`
  ).join("") : '<li class="empty-note" style="background:none;">Inget väntar på dig.</li>';

  document.getElementById("outgoingInviteList").innerHTML = outgoing.length ? outgoing.map(([p, s]) => {
    if (s.status === "pending_signup") {
      return `<li><div class="li-main"><span style="font-size:1.4rem;">${emojiFor(p)}</span><div>${p.filename}<div class="muted">bjöd in ${s.toEmail} · ${icon(termsIcon(s.terms))}${termsLabel(s.terms)}</div></div></div>
        <div class="li-actions"><button class="btn small ghost" onclick="simulateSignup('${p.id}','${s.id}')">${icon("bolt")}simulera: personen registrerar sig</button></div></li>`;
    }
    return `<li><div class="li-main"><span style="font-size:1.4rem;">${emojiFor(p)}</span><div>${p.filename}<div class="muted">delningslänk skapad, inte öppnad än · ${icon(termsIcon(s.terms))}${termsLabel(s.terms)}</div></div></div>
      <div class="li-actions"><span class="muted">öppnas från bildens detaljpanel</span></div></li>`;
  }).join("") : '<li class="empty-note" style="background:none;">Inga obehandlade inbjudningar.</li>';

  document.getElementById("sharedByMeList").innerHTML = sharedByMe.length ? sharedByMe.map(([p, s]) =>
    `<li><div class="li-main"><span style="font-size:1.4rem;">${emojiFor(p)}</span><div>${p.filename}<div class="muted">med ${userName(s.toUserId)} · ${icon(termsIcon(s.terms))}${termsLabel(s.terms)}</div></div></div>
     <div class="li-actions">${s.terms === "strict"
        ? `<button class="btn small danger" onclick="revokeShare('${p.id}','${s.id}')">${icon("delete")}Återkalla</button>`
        : `<span class="muted">kan inte återkallas</span>`}</div></li>`
  ).join("") : '<li class="empty-note" style="background:none;">Du har inte delat något än.</li>';
}

function updatePendingBadge() {
  const n = DB.photos.reduce((acc, p) => acc + p.shares.filter((s) => s.toUserId === currentUserId && s.status === "pending_accept").length, 0);
  const badge = document.getElementById("pendingCount");
  badge.textContent = n;
  badge.classList.toggle("hidden", n === 0);
}

function acceptIncoming(photoId, shareId) {
  const p = DB.photos.find((x) => x.id === photoId);
  const s = p.shares.find((x) => x.id === shareId);
  s.status = "active";
  toast(`Accepterade "${p.filename}" — finns nu i ditt galleri.`);
  render();
}
function declineIncoming(photoId, shareId) {
  const p = DB.photos.find((x) => x.id === photoId);
  const s = p.shares.find((x) => x.id === shareId);
  s.status = "declined";
  toast(`Nekade "${p.filename}".`);
  render();
}
function revokeShare(photoId, shareId) {
  const p = DB.photos.find((x) => x.id === photoId);
  const s = p.shares.find((x) => x.id === shareId);
  const who = userName(s.toUserId);
  s.status = "revoked";
  toast(`Återkallade ${who}s åtkomst till "${p.filename}".`);
  render();
}
function simulateSignup(photoId, shareId) {
  const p = DB.photos.find((x) => x.id === photoId);
  const s = p.shares.find((x) => x.id === shareId);
  let user = Object.values(DB.users).find((u) => u.email === s.toEmail);
  if (!user) {
    const id = "u" + nextUserSeq++;
    const local = s.toEmail.split("@")[0];
    const name = local.charAt(0).toUpperCase() + local.slice(1);
    user = { id, name, username: local, email: s.toEmail };
    DB.users[id] = user;
  }
  s.toUserId = user.id;
  s.status = "active";
  toast(`${s.toEmail} registrerade sig — den väntande delningen löstes automatiskt in i ${user.name}s galleri.`);
  render();
}
function simulateOpenLink(photoId, shareId, asUserId) {
  const p = DB.photos.find((x) => x.id === photoId);
  const s = p.shares.find((x) => x.id === shareId);
  s.toUserId = asUserId;
  s.status = "pending_accept";
  toast(`Simulerat: ${userName(asUserId)} öppnade länken medan hen var inloggad — finns nu i hens väntande inkorg.`);
  render();
}

function shareViaUsername(photoId, username, terms) {
  const p = DB.photos.find((x) => x.id === photoId);
  const target = Object.values(DB.users).find((u) => u.username === username && !u.isEventAccount);
  const statusEl = document.getElementById("shareStatus");
  if (!target) {
    statusEl.textContent = `Ingen användare hittades för "${username}".`;
    statusEl.className = "status-msg err";
    return;
  }
  if (target.id === p.ownerId) {
    statusEl.textContent = "Det är redan ägaren.";
    statusEl.className = "status-msg err";
    return;
  }
  p.shares.push({ id: "s" + nextShareSeq++, kind: "username", toUserId: target.id, terms, status: "active", sharedByUserId: currentUserId });
  statusEl.textContent = `Delad med ${target.name} (${termsLabel(terms)}).`;
  statusEl.className = "status-msg ok";
  toast(`Delade "${p.filename}" med ${target.name}.`);
  render();
}
function shareViaEmail(photoId, email, terms) {
  const p = DB.photos.find((x) => x.id === photoId);
  const statusEl = document.getElementById("shareStatus");
  if (!email || !email.includes("@")) {
    statusEl.textContent = "Ange en giltig e-postadress.";
    statusEl.className = "status-msg err";
    return;
  }
  p.shares.push({ id: "s" + nextShareSeq++, kind: "email", toEmail: email, terms, status: "pending_signup", sharedByUserId: currentUserId });
  statusEl.textContent = `Inbjudan skickad till ${email} — löses automatiskt när personen registrerar sig.`;
  statusEl.className = "status-msg ok";
  toast(`Bjöd in ${email} till "${p.filename}".`);
  render();
}
function shareViaPlatform(photoId, terms) {
  const p = DB.photos.find((x) => x.id === photoId);
  const token = "tok_" + Math.random().toString(36).slice(2, 8);
  const share = { id: "s" + nextShareSeq++, kind: "platform", toUserId: null, toEmail: null, terms, status: "link_open_pending", token, sharedByUserId: currentUserId };
  p.shares.push(share);
  const link = `https://dpfas.local/s/${token}`;
  const statusEl = document.getElementById("shareStatus");
  const finish = (via) => {
    statusEl.innerHTML = `Länk skapad (${via}): <code>${link}</code><br>Att öppna den utloggad leder till registrering; att öppna den redan inloggad visar den som en väntande delning att acceptera.`;
    statusEl.className = "status-msg ok";
    render();
    openShareModal(photoId); // rendera om modalen för att visa "simulera öppning"
  };
  if (navigator.share) {
    navigator.share({ title: `DPFAS — ${p.filename}`, text: `Delad via DPFAS (${termsLabel(terms)})`, url: link })
      .then(() => finish("enhetens delningsmeny")).catch(() => finish("delningsmenyn stängdes"));
  } else {
    finish("Web Share API saknas — länken visas direkt");
  }
}

function openShareModal(photoId) {
  const p = DB.photos.find((x) => x.id === photoId);
  const others = Object.values(DB.users).filter((u) => !u.isEventAccount && u.id !== currentUserId);
  const pendingLinks = p.shares.filter((s) => s.kind === "platform" && s.status === "link_open_pending");
  document.getElementById("shareModalBody").innerHTML = `
    <button class="lb-btn lb-close" onclick="closeShareModal()">${icon("close")}</button>
    <h2>${icon("share")}Dela "${p.filename}"</h2>
    <div class="mock-field">
      <label>Villkor</label>
      <div class="seg" id="shareTermsSeg">
        <button data-terms="free" aria-pressed="true" onclick="setShareTerms(this,'free')">${icon("public")}Fri</button>
        <button data-terms="strict" aria-pressed="false" onclick="setShareTerms(this,'strict')">${icon("lock")}Strikt</button>
      </div>
    </div>
    <div class="mock-field">
      <label>Metod</label>
      <div class="seg" id="shareMethodSeg">
        <button data-method="platform" aria-pressed="true" onclick="setShareMethod('${photoId}',this,'platform')">${icon("ios_share")}Delningsmeny</button>
        <button data-method="username" aria-pressed="false" onclick="setShareMethod('${photoId}',this,'username')">${icon("person")}Användarnamn</button>
        <button data-method="email" aria-pressed="false" onclick="setShareMethod('${photoId}',this,'email')">${icon("mail")}E-post</button>
      </div>
    </div>
    <div id="shareMethodBody"></div>
    <div class="status-msg" id="shareStatus"></div>
    ${pendingLinks.length ? `<div class="hint" style="margin-top:0.8rem;">${icon("science")}utvecklarläge: simulera att den senaste länken öppnas medan man är inloggad som —
      ${others.map((u) => `<button class="btn small ghost" onclick="simulateOpenLink('${photoId}','${pendingLinks[pendingLinks.length - 1].id}','${u.id}')">${u.name}</button>`).join(" ")}
      </div>` : ""}
  `;
  document.getElementById("shareModal").classList.remove("hidden");
  renderShareMethodBody(photoId, "platform");
}
function closeShareModal() { document.getElementById("shareModal").classList.add("hidden"); }
function setShareTerms(btn, terms) {
  btn.parentElement.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", "false"));
  btn.setAttribute("aria-pressed", "true");
}
function currentShareTerms() {
  return document.querySelector('#shareTermsSeg button[aria-pressed="true"]').dataset.terms;
}
function setShareMethod(photoId, btn, method) {
  btn.parentElement.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", "false"));
  btn.setAttribute("aria-pressed", "true");
  renderShareMethodBody(photoId, method);
}
function renderShareMethodBody(photoId, method) {
  const body = document.getElementById("shareMethodBody");
  if (method === "platform") {
    body.innerHTML = `<p class="hint">Skapar en token + länk och öppnar sedan enhetens riktiga delningsmeny om den finns.</p>
      <div class="row"><button class="btn primary" onclick="shareViaPlatform('${photoId}', currentShareTerms())">${icon("ios_share")}Skapa &amp; dela</button></div>`;
  } else if (method === "username") {
    body.innerHTML = `<div class="mock-field"><label>DPFAS-användarnamn</label><input type="text" id="shareUsernameInput" placeholder="elisabeth (testa en felstavning för att se 'hittades inte')"></div>
      <div class="row"><button class="btn primary" onclick="shareViaUsername('${photoId}', document.getElementById('shareUsernameInput').value.trim(), currentShareTerms())">${icon("send")}Skicka</button></div>`;
  } else {
    body.innerHTML = `<div class="mock-field"><label>E-postadress</label><input type="email" id="shareEmailInput" placeholder="ny@example.com"></div>
      <div class="row"><button class="btn primary" onclick="shareViaEmail('${photoId}', document.getElementById('shareEmailInput').value.trim(), currentShareTerms())">${icon("send")}Skicka inbjudan</button></div>`;
  }
}

// ----------------------------------------------------------- photo detail

function openPhotoDetail(photoId) {
  openPhotoId = photoId;
  renderPhotoDetail(photoId);
  document.getElementById("photoDetail").classList.remove("hidden");
}
function closePhotoDetail() {
  openPhotoId = null;
  document.getElementById("photoDetail").classList.add("hidden");
}
function renderPhotoDetail(photoId) {
  const p = DB.photos.find((x) => x.id === photoId);
  if (!p) return;
  const iOwn = p.ownerId === currentUserId;
  const myShare = activeShareFor(p, currentUserId);
  const dl = canDownload(p, currentUserId);

  let accessHtml;
  if (iOwn) {
    const activeShares = p.shares.filter((s) => s.status === "active");
    accessHtml = `<p>Du äger den här bilden.</p>` + (activeShares.length ? `
      <div>${activeShares.map((s) => `
        <div class="share-row"><span>${s.toUserId ? userName(s.toUserId) : s.toEmail} — <span class="chip ${s.terms}" style="position:static;">${icon(termsIcon(s.terms))}${termsLabel(s.terms)}</span></span>
        ${s.terms === "strict" ? `<button class="btn small danger" onclick="revokeShare('${p.id}','${s.id}')">${icon("delete")}Återkalla</button>` : `<span class="muted">kan inte återkallas</span>`}</div>`).join("")}
      </div>` : `<p class="muted">Inte delad med någon än.</p>`);
  } else if (myShare) {
    accessHtml = myShare.terms === "free"
      ? `<p>Delad med dig av ${userName(p.ownerId)} — <b>${termsLabel("free")}</b>: full åtkomst, du kan ladda ner och dela vidare. Kan inte återkallas.</p>`
      : `<p>Delad med dig av ${userName(p.ownerId)} — <b>${termsLabel("strict")}</b>: bara visning + taggning. Nedladdning och vidaredelning är blockerat, och ${userName(p.ownerId)} kan återkalla detta när som helst.</p>`;
  } else {
    accessHtml = `<p class="muted">Inte delad med dig.</p>`;
  }

  document.getElementById("photoDetailBody").innerHTML = `
    <button class="lb-btn lb-close" onclick="closePhotoDetail()">${icon("close")}</button>
    <div class="detail-hero" style="background:${colorFor(p.id)}">${emojiFor(p)}</div>
    <h2>${p.filename}</h2>
    <div class="tag-row">
      ${p.tags.map((t, i) => `<span class="tag-pill">${escapeHtml(t.text)}${t.endorsedBy.length ? ` &middot; +${t.endorsedBy.length}` : ""}
        ${t.by !== currentUserId && !t.endorsedBy.includes(currentUserId) && (iOwn || myShare) ? ` <button class="endorse-link" onclick="endorseTag('${p.id}',${i})">${icon("verified")}bekräfta</button>` : ""}
      </span>`).join("")}
    </div>
    <h3>${icon("person")}Ägare</h3>
    <p>${userName(p.ownerId)}${iOwn ? " (du)" : ""}</p>
    <h3>${icon("lock_open")}Åtkomst</h3>
    ${accessHtml}
    <div class="row" style="margin-top:1rem;">
      <button class="btn ${dl ? "good" : "ghost"}" ${dl ? "" : "disabled"} onclick="mockDownload('${p.id}')" title="${dl ? "" : "Blockerat av strikta villkor, eller inte delad med dig"}">${icon("download")}Ladda ner</button>
      ${canManageSharing(p, currentUserId) ? `<button class="btn primary" onclick="openShareModal('${p.id}')">${icon("share")}Dela</button>` : ""}
    </div>
  `;
}
function endorseTag(photoId, tagIndex) {
  const p = DB.photos.find((x) => x.id === photoId);
  const t = p.tags[tagIndex];
  if (!t.endorsedBy.includes(currentUserId)) t.endorsedBy.push(currentUserId);
  renderPhotoDetail(photoId);
}
function mockDownload(photoId) {
  const p = DB.photos.find((x) => x.id === photoId);
  toast(`(mock) laddar ner "${p.filename}" — ingen riktig fil, det här är en prototyp.`);
}

// ---------------------------------------------------------------- events

function renderEvents() {
  const ev = DB.events[0];
  const acct = DB.users[ev.accountId];
  document.getElementById("eventCard").innerHTML = `
    <h3 style="margin-top:0;">${ev.name}</h3>
    <p class="section-sub small">Värd: ${userName(ev.hostUserId)} &middot; eventkonto: ${acct.username}</p>
    <div class="axis">
      <div class="axis-info"><div class="axis-name">${icon("upload_file")}Uppladdningsåtkomst</div><p class="axis-desc">Vem som får bidra till eventets album</p></div>
      <div class="seg">
        ${["pre-approved", "free-for-all", "register-approve"].map((v, i) =>
          `<button aria-pressed="${ev.axes.uploadAccess === v}" onclick="setEventAxis('uploadAccess','${v}')">${["Förgodkänd", "Fritt fram", "Registrera → godkänn"][i]}</button>`
        ).join("")}
      </div>
    </div>
    <div class="axis">
      <div class="axis-info"><div class="axis-name">${icon("visibility")}Synlighetsomfång</div><p class="axis-desc">Vad gäster ser, oberoende av vem som laddade upp</p></div>
      <div class="seg">
        ${["all", "curated"].map((v, i) =>
          `<button aria-pressed="${ev.axes.visibility === v}" onclick="setEventAxis('visibility','${v}')">${["Alla uppladdningar", "Utvalt urval"][i]}</button>`
        ).join("")}
      </div>
    </div>
    <div class="axis">
      <div class="axis-info"><div class="axis-name">${icon("tv")}Live-vägg på TV-skärm</div><p class="axis-desc">En separat visningskanal — inte en synlighetsinställning</p></div>
      <button class="toggle" aria-pressed="${ev.axes.tv}" onclick="toggleTv()"></button>
    </div>
  `;
  document.getElementById("tvWallWrap").classList.toggle("hidden", !ev.axes.tv);
  renderTvWall();
  renderEventPool();
}
function setEventAxis(axis, value) {
  const ev = DB.events[0];
  ev.axes[axis] = value;
  const messages = {
    uploadAccess: { "free-for-all": "Vem som helst med länken/QR-koden kan nu ladda upp, inget konto krävs.", "pre-approved": "Bara gäster värden bjudit in i förväg kan ladda upp nu.", "register-approve": "Gäster kan begära åtkomst; uppladdningar räknas när värden godkänt dem." },
    visibility: { all: "Gäster ser nu alla uppladdningar.", curated: "Gäster ser nu bara det utvalda urvalet." },
  };
  toast(messages[axis][value]);
  renderEvents();
}
function toggleTv() {
  const ev = DB.events[0];
  ev.axes.tv = !ev.axes.tv;
  toast(ev.axes.tv ? "TV-väggen är nu live." : "TV-väggen är avstängd.");
  renderEvents();
}
function eventPhotos() { return DB.photos.filter((p) => p.isEventPhoto); }
function renderTvWall() {
  const ev = DB.events[0];
  const shown = eventPhotos().filter((p) => ev.axes.visibility === "all" || p.curated);
  document.getElementById("tvWallGrid").innerHTML = shown.map((p) => thumbHtml(p, { curatedChip: true })).join("");
}
function renderEventPool() {
  document.getElementById("eventPoolGrid").innerHTML = eventPhotos().map((p) => `
    <div class="thumb ${p.curated ? "curated" : ""}" style="background:${colorFor(p.id)}" onclick="toggleCurated('${p.id}')">
      <span class="emoji">${emojiFor(p)}</span>
      ${p.curated ? `<span class="chip curated">${icon("star")}Kurerad</span>` : ""}
      <span class="fname">${p.filename}</span>
    </div>`).join("");
}
function toggleCurated(photoId) {
  const p = DB.photos.find((x) => x.id === photoId);
  p.curated = !p.curated;
  toast(`${p.filename} ${p.curated ? "lades till i" : "togs bort från"} det kuraterade urvalet.`);
  renderEvents();
}

// ---------------------------------------------------------- guest upload

let guestSelectedPool = new Set();
function openGuestUpload() {
  document.getElementById("guestUploadScreen").classList.remove("hidden");
  renderGuestUpload();
}
function closeGuestUpload() { document.getElementById("guestUploadScreen").classList.add("hidden"); }
function requestEventAccess() {
  const ev = DB.events[0];
  const typed = document.getElementById("guestRegisterName").value.trim();
  const name = escapeHtml(typed || "Du");
  document.getElementById("guestUploadBody").innerHTML =
    `<h2>${ev.name}</h2><p>Begäran skickad för ${name} — dina uppladdningar visas när ${userName(ev.hostUserId)} har godkänt dig.</p>`;
}
function renderGuestUpload() {
  const ev = DB.events[0];
  const body = document.getElementById("guestUploadBody");
  if (ev.axes.uploadAccess === "pre-approved") {
    body.innerHTML = `<h2>${ev.name}</h2><p>Det här eventet tar bara emot uppladdningar från personer värden bjudit in i förväg. Be ${userName(ev.hostUserId)} om en inbjudan.</p>`;
    return;
  }
  if (ev.axes.uploadAccess === "register-approve") {
    body.innerHTML = `<h2>${ev.name}</h2>
      <p>Registrera dig för att begära uppladdningsåtkomst — värden godkänner varje registrering innan uppladdningar räknas.</p>
      <div class="mock-field"><label>Ditt namn</label><input type="text" id="guestRegisterName" placeholder="Gästens namn"></div>
      <div class="row"><button class="btn primary" onclick="requestEventAccess()">${icon("how_to_reg")}Begär åtkomst</button></div>`;
    return;
  }
  // fritt fram
  guestSelectedPool = new Set();
  body.innerHTML = `<h2>${ev.name}</h2>
    <p class="hint">Inget konto krävs. Bilder du laddar upp här ägs av eventets eget konto (${DB.users[ev.accountId].username}), aldrig av dig som anonym gäst — se EVENTS.md:s lösta ägarskapsbeslut.</p>
    <div class="mock-field"><label>Välj filer</label><div class="file-pool" id="guestFilePool"></div></div>
    <div class="row"><button class="btn primary" id="guestUploadBtn" disabled onclick="doGuestUpload()">${icon("upload")}Ladda upp (<span id="guestSelectedCount">0</span> valda)</button></div>
    <div class="status-msg" id="guestUploadStatus"></div>`;
  renderGuestPool();
}
function renderGuestPool() {
  const poolEl = document.getElementById("guestFilePool");
  if (!pool.length) {
    poolEl.innerHTML = '<p class="empty-note">Inga fler exempelbilder den här sessionen.</p>';
  } else {
    poolEl.innerHTML = pool.map((f) =>
      `<div class="pool-item ${guestSelectedPool.has(f.poolId) ? "selected" : ""}" style="background:${colorFor(f.poolId)}" onclick="toggleGuestPoolItem('${f.poolId}')" title="${f.filename}">${f.emoji}</div>`
    ).join("");
  }
  document.getElementById("guestSelectedCount").textContent = guestSelectedPool.size;
  document.getElementById("guestUploadBtn").disabled = guestSelectedPool.size === 0;
}
function toggleGuestPoolItem(poolId) {
  if (guestSelectedPool.has(poolId)) guestSelectedPool.delete(poolId);
  else guestSelectedPool.add(poolId);
  renderGuestPool();
}
function doGuestUpload() {
  const ev = DB.events[0];
  const chosen = pool.filter((f) => guestSelectedPool.has(f.poolId));
  chosen.forEach((f) => {
    DB.photos.push(mkPhoto(f.filename, EVENT_TAG, ev.accountId, [{ text: EVENT_TAG, by: ev.accountId }], { isEventPhoto: true, curated: false }));
  });
  pool = pool.filter((f) => !guestSelectedPool.has(f.poolId));
  const count = chosen.length;
  guestSelectedPool.clear();
  document.getElementById("guestUploadStatus").innerHTML = `Laddade upp ${count} bild${count === 1 ? "" : "er"}, ägda av <b>${DB.users[ev.accountId].username}</b> (eventkontot) — inte av dig.`;
  document.getElementById("guestUploadStatus").className = "status-msg ok";
  renderGuestPool();
  render();
}

// -------------------------------------------------------------------- init

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("#tabNav .nav-pill").forEach((b) => b.addEventListener("click", () => switchTab(b.dataset.tab)));
  document.getElementById("pendingBtn").addEventListener("click", () => switchTab("sharing"));
  document.getElementById("userSwitch").addEventListener("change", (e) => switchUser(e.target.value));
  document.getElementById("batchName").addEventListener("input", renderUpload);
  document.getElementById("uploadBtn").addEventListener("click", doUpload);
  document.getElementById("openGuestUploadBtn").addEventListener("click", openGuestUpload);
  document.getElementById("guestCloseBtn").addEventListener("click", closeGuestUpload);
  document.querySelectorAll(".overlay").forEach((el) => el.addEventListener("click", (e) => { if (e.target === el) el.classList.add("hidden"); }));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") document.querySelectorAll(".overlay").forEach((el) => el.classList.add("hidden"));
  });
  render();
});
