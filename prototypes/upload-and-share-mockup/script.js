// Client-side only. Everything here is a fake in-memory database that real
// clicks actually mutate — no server, nothing leaves this page. See
// documentation/upload-and-share/ for the design this demonstrates.

// ---------------------------------------------------------------- seed data

const DB = {
  users: {
    u1: { id: "u1", name: "Joakim", username: "joakim", email: "joakim.reuterborg@gmail.com" },
    u2: { id: "u2", name: "Elisabeth", username: "elisabeth", email: "elisabeth.reuterborg@gmail.com" },
    ev1acct: { id: "ev1acct", name: "Anna & Erik's Wedding (event account)", username: "event-annaerik", email: null, isEventAccount: true },
  },
  photos: [],
  events: [
    { id: "ev1", name: "Anna & Erik's Wedding", hostUserId: "u1", accountId: "ev1acct",
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
  mkPhoto("beach1.jpg", "Summer 2019", "u1", [{ text: "Summer 2019", by: "u1" }, { text: "Beach", by: "u1" }], {
    shares: [{ id: "s" + nextShareSeq++, kind: "username", toUserId: "u2", terms: "strict", status: "active", sharedByUserId: "u1" }],
  }),
  mkPhoto("cake.jpg", "Summer 2019", "u1", [{ text: "Summer 2019", by: "u1" }, { text: "Birthday", by: "u1" }]),
  mkPhoto("mountain.jpg", "Hiking trip", "u2", [{ text: "Hiking trip", by: "u2" }], {
    shares: [{ id: "s" + nextShareSeq++, kind: "username", toUserId: "u1", terms: "free", status: "active", sharedByUserId: "u2" }],
  }),
  mkPhoto("loki.jpg", "Hiking trip", "u2", [{ text: "Hiking trip", by: "u2" }, { text: "Loki", by: "u2" }], {
    shares: [{ id: "s" + nextShareSeq++, kind: "username", toUserId: "u1", terms: "strict", status: "active", sharedByUserId: "u2" }],
  }),
  mkPhoto("sunset.jpg", "web-upload-elisabeth-20260601", "u2", [{ text: "web-upload-elisabeth-20260601", by: "u2" }], {
    shares: [{ id: "s" + nextShareSeq++, kind: "email", toEmail: "anna.friend@example.com", terms: "free", status: "pending_signup", sharedByUserId: "u2" }],
  }),
  mkPhoto("christmas.jpg", "Christmas 2025", "u1", [{ text: "Christmas 2025", by: "u1" }, { text: "Kids", by: "u1" }], {
    shares: [{ id: "s" + nextShareSeq++, kind: "platform", toUserId: null, toEmail: null, terms: "free", status: "link_open_pending", token: "tok_9f2a", sharedByUserId: "u1" }],
  }),
  mkPhoto("snow.jpg", "Christmas 2025", "u1", [{ text: "Christmas 2025", by: "u1" }]),
  mkPhoto("puppy2.jpg", "Hiking trip", "u2", [{ text: "Hiking trip", by: "u2" }, { text: "Loki again", by: "u2" }])
);

const EVENT_TAG = "Anna & Erik's Wedding";
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
function userName(id) { return DB.users[id] ? DB.users[id].name : "(unknown)"; }

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
  if (photo.ownerId === currentUserId) chip = '<span class="chip owner">Yours</span>';
  else {
    const s = activeShareFor(photo, currentUserId);
    if (s) chip = `<span class="chip ${s.terms}">${s.terms}</span>`;
  }
  if (opts.curatedChip && photo.curated) chip += '<span class="chip curated" style="right:auto;left:0.4rem;">Curated</span>';
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
    : "No photos yet for " + me().name + " — upload some, or accept/receive a share.";
}

// --------------------------------------------------------------- upload

function renderUpload() {
  document.getElementById("batchDefaultHint").textContent =
    "Empty name → catalogue = web-upload-" + me().username + "-{timestamp}";
  const poolEl = document.getElementById("filePool");
  if (!pool.length) {
    poolEl.innerHTML = '<p class="empty-note">No more stock photos this session — reload the page to reset.</p>';
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
  toast(`Uploaded ${count} photo${count === 1 ? "" : "s"} as "${batch}"`);
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
    `<li><div class="li-main"><span style="font-size:1.4rem;">${emojiFor(p)}</span><div>${p.filename}<div class="muted">from ${userName(s.sharedByUserId)} · ${s.terms} · via platform-share link</div></div></div>
     <div class="li-actions"><button class="btn small good" onclick="acceptIncoming('${p.id}','${s.id}')">Accept</button><button class="btn small ghost" onclick="declineIncoming('${p.id}','${s.id}')">Decline</button></div></li>`
  ).join("") : '<li class="empty-note" style="background:none;">Nothing waiting on you.</li>';

  document.getElementById("outgoingInviteList").innerHTML = outgoing.length ? outgoing.map(([p, s]) => {
    if (s.status === "pending_signup") {
      return `<li><div class="li-main"><span style="font-size:1.4rem;">${emojiFor(p)}</span><div>${p.filename}<div class="muted">invited ${s.toEmail} · ${s.terms}</div></div></div>
        <div class="li-actions"><button class="btn small ghost" onclick="simulateSignup('${p.id}','${s.id}')">🔧 simulate: they sign up</button></div></li>`;
    }
    return `<li><div class="li-main"><span style="font-size:1.4rem;">${emojiFor(p)}</span><div>${p.filename}<div class="muted">platform link generated, not opened yet · ${s.terms}</div></div></div>
      <div class="li-actions"><span class="muted">open from the photo's detail panel</span></div></li>`;
  }).join("") : '<li class="empty-note" style="background:none;">No outstanding invites.</li>';

  document.getElementById("sharedByMeList").innerHTML = sharedByMe.length ? sharedByMe.map(([p, s]) =>
    `<li><div class="li-main"><span style="font-size:1.4rem;">${emojiFor(p)}</span><div>${p.filename}<div class="muted">with ${userName(s.toUserId)} · ${s.terms}</div></div></div>
     <div class="li-actions">${s.terms === "strict"
        ? `<button class="btn small danger" onclick="revokeShare('${p.id}','${s.id}')">Revoke</button>`
        : `<span class="muted">irrevocable</span>`}</div></li>`
  ).join("") : '<li class="empty-note" style="background:none;">You haven\'t shared anything yet.</li>';
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
  toast(`Accepted "${p.filename}" — now in your gallery.`);
  render();
}
function declineIncoming(photoId, shareId) {
  const p = DB.photos.find((x) => x.id === photoId);
  const s = p.shares.find((x) => x.id === shareId);
  s.status = "declined";
  toast(`Declined "${p.filename}".`);
  render();
}
function revokeShare(photoId, shareId) {
  const p = DB.photos.find((x) => x.id === photoId);
  const s = p.shares.find((x) => x.id === shareId);
  const who = userName(s.toUserId);
  s.status = "revoked";
  toast(`Revoked ${who}'s access to "${p.filename}".`);
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
  toast(`${s.toEmail} signed up — pending share resolved automatically into ${user.name}'s gallery.`);
  render();
}
function simulateOpenLink(photoId, shareId, asUserId) {
  const p = DB.photos.find((x) => x.id === photoId);
  const s = p.shares.find((x) => x.id === shareId);
  s.toUserId = asUserId;
  s.status = "pending_accept";
  toast(`Simulated: ${userName(asUserId)} opened the link while logged in — now in their Pending inbox.`);
  render();
}

function shareViaUsername(photoId, username, terms) {
  const p = DB.photos.find((x) => x.id === photoId);
  const target = Object.values(DB.users).find((u) => u.username === username && !u.isEventAccount);
  const statusEl = document.getElementById("shareStatus");
  if (!target) {
    statusEl.textContent = `No user found for "${username}".`;
    statusEl.className = "status-msg err";
    return;
  }
  if (target.id === p.ownerId) {
    statusEl.textContent = "That's already the owner.";
    statusEl.className = "status-msg err";
    return;
  }
  p.shares.push({ id: "s" + nextShareSeq++, kind: "username", toUserId: target.id, terms, status: "active", sharedByUserId: currentUserId });
  statusEl.textContent = `Shared with ${target.name} (${terms}).`;
  statusEl.className = "status-msg ok";
  toast(`Shared "${p.filename}" with ${target.name}.`);
  render();
}
function shareViaEmail(photoId, email, terms) {
  const p = DB.photos.find((x) => x.id === photoId);
  const statusEl = document.getElementById("shareStatus");
  if (!email || !email.includes("@")) {
    statusEl.textContent = "Enter a valid email address.";
    statusEl.className = "status-msg err";
    return;
  }
  p.shares.push({ id: "s" + nextShareSeq++, kind: "email", toEmail: email, terms, status: "pending_signup", sharedByUserId: currentUserId });
  statusEl.textContent = `Invite sent to ${email} — resolves automatically once they sign up.`;
  statusEl.className = "status-msg ok";
  toast(`Invited ${email} to "${p.filename}".`);
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
    statusEl.innerHTML = `Link generated (${via}): <code>${link}</code><br>Opening it while logged out prompts signup; opening it while already logged in shows it as a pending share to accept.`;
    statusEl.className = "status-msg ok";
    render();
    openShareModal(photoId); // re-render modal to show the simulate-open affordance
  };
  if (navigator.share) {
    navigator.share({ title: `DPFAS — ${p.filename}`, text: `Shared via DPFAS (${terms})`, url: link })
      .then(() => finish("your device's share sheet")).catch(() => finish("share sheet dismissed"));
  } else {
    finish("Web Share API unavailable — link shown directly");
  }
}

function openShareModal(photoId) {
  const p = DB.photos.find((x) => x.id === photoId);
  const others = Object.values(DB.users).filter((u) => !u.isEventAccount && u.id !== currentUserId);
  const pendingLinks = p.shares.filter((s) => s.kind === "platform" && s.status === "link_open_pending");
  document.getElementById("shareModalBody").innerHTML = `
    <button class="lb-btn lb-close" onclick="closeShareModal()">&#10005;</button>
    <h2>Share "${p.filename}"</h2>
    <div class="mock-field">
      <label>Terms</label>
      <div class="seg" id="shareTermsSeg">
        <button data-terms="free" aria-pressed="true" onclick="setShareTerms(this,'free')">Free</button>
        <button data-terms="strict" aria-pressed="false" onclick="setShareTerms(this,'strict')">Strict</button>
      </div>
    </div>
    <div class="mock-field">
      <label>Method</label>
      <div class="seg" id="shareMethodSeg">
        <button data-method="platform" aria-pressed="true" onclick="setShareMethod('${photoId}',this,'platform')">Platform share sheet</button>
        <button data-method="username" aria-pressed="false" onclick="setShareMethod('${photoId}',this,'username')">Username</button>
        <button data-method="email" aria-pressed="false" onclick="setShareMethod('${photoId}',this,'email')">Email invite</button>
      </div>
    </div>
    <div id="shareMethodBody"></div>
    <div class="status-msg" id="shareStatus"></div>
    ${pendingLinks.length ? `<div class="hint" style="margin-top:0.8rem;">🔧 dev: simulate opening the last generated link while logged in as —
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
    body.innerHTML = `<p class="hint">Generates a token + link, then invokes your device's real share sheet if available.</p>
      <div class="row"><button class="btn primary" onclick="shareViaPlatform('${photoId}', currentShareTerms())">Generate &amp; share</button></div>`;
  } else if (method === "username") {
    body.innerHTML = `<div class="mock-field"><label>DPFAS username</label><input type="text" id="shareUsernameInput" placeholder="elisabeth (try a typo to see 'not found')"></div>
      <div class="row"><button class="btn primary" onclick="shareViaUsername('${photoId}', document.getElementById('shareUsernameInput').value.trim(), currentShareTerms())">Send</button></div>`;
  } else {
    body.innerHTML = `<div class="mock-field"><label>Email address</label><input type="email" id="shareEmailInput" placeholder="new@example.com"></div>
      <div class="row"><button class="btn primary" onclick="shareViaEmail('${photoId}', document.getElementById('shareEmailInput').value.trim(), currentShareTerms())">Send invite</button></div>`;
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
    accessHtml = `<p>You own this photo.</p>` + (activeShares.length ? `
      <div>${activeShares.map((s) => `
        <div class="share-row"><span>${s.toUserId ? userName(s.toUserId) : s.toEmail} — <span class="chip ${s.terms}" style="position:static;">${s.terms}</span></span>
        ${s.terms === "strict" ? `<button class="btn small danger" onclick="revokeShare('${p.id}','${s.id}')">Revoke</button>` : `<span class="muted">irrevocable</span>`}</div>`).join("")}
      </div>` : `<p class="muted">Not shared with anyone yet.</p>`);
  } else if (myShare) {
    accessHtml = myShare.terms === "free"
      ? `<p>Shared with you by ${userName(p.ownerId)} — <b>free</b>: full access, you can download and reshare. Not revocable.</p>`
      : `<p>Shared with you by ${userName(p.ownerId)} — <b>strict</b>: view + tag only. Download and resharing are blocked, and ${userName(p.ownerId)} can revoke this at any time.</p>`;
  } else {
    accessHtml = `<p class="muted">Not shared with you.</p>`;
  }

  document.getElementById("photoDetailBody").innerHTML = `
    <button class="lb-btn lb-close" onclick="closePhotoDetail()">&#10005;</button>
    <div class="detail-hero" style="background:${colorFor(p.id)}">${emojiFor(p)}</div>
    <h2>${p.filename}</h2>
    <div class="tag-row">
      ${p.tags.map((t, i) => `<span class="tag-pill">${t.text}${t.endorsedBy.length ? ` &middot; +${t.endorsedBy.length}` : ""}
        ${t.by !== currentUserId && !t.endorsedBy.includes(currentUserId) && (iOwn || myShare) ? ` <a href="#" onclick="endorseTag('${p.id}',${i});return false;">endorse</a>` : ""}
      </span>`).join("")}
    </div>
    <h3>Owner</h3>
    <p>${userName(p.ownerId)}${iOwn ? " (you)" : ""}</p>
    <h3>Access</h3>
    ${accessHtml}
    <div class="row" style="margin-top:1rem;">
      <button class="btn ${dl ? "good" : "ghost"}" ${dl ? "" : "disabled"} onclick="mockDownload('${p.id}')" title="${dl ? "" : "Blocked by strict terms, or not shared with you"}">Download</button>
      ${canManageSharing(p, currentUserId) ? `<button class="btn primary" onclick="openShareModal('${p.id}')">Share</button>` : ""}
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
  toast(`(mock) downloading "${p.filename}" — no real file, this is a prototype.`);
}

// ---------------------------------------------------------------- events

function renderEvents() {
  const ev = DB.events[0];
  const acct = DB.users[ev.accountId];
  document.getElementById("eventCard").innerHTML = `
    <h3 style="margin-top:0;">${ev.name}</h3>
    <p class="section-sub small">Hosted by ${userName(ev.hostUserId)} &middot; event account: ${acct.username}</p>
    <div class="axis">
      <div class="axis-info"><div class="axis-name">Upload access</div><p class="axis-desc">Who may contribute to this event's album</p></div>
      <div class="seg">
        ${["pre-approved", "free-for-all", "register-approve"].map((v, i) =>
          `<button aria-pressed="${ev.axes.uploadAccess === v}" onclick="setEventAxis('uploadAccess','${v}')">${["Pre-approved", "Free-for-all", "Register → approve"][i]}</button>`
        ).join("")}
      </div>
    </div>
    <div class="axis">
      <div class="axis-info"><div class="axis-name">Visibility scope</div><p class="axis-desc">What invitees browse, independent of who uploaded</p></div>
      <div class="seg">
        ${["all", "curated"].map((v, i) =>
          `<button aria-pressed="${ev.axes.visibility === v}" onclick="setEventAxis('visibility','${v}')">${["All uploads", "Curated best-of"][i]}</button>`
        ).join("")}
      </div>
    </div>
    <div class="axis">
      <div class="axis-info"><div class="axis-name">Live TV-screen wall</div><p class="axis-desc">A separate output channel — not a visibility setting</p></div>
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
    uploadAccess: { "free-for-all": "Anyone with the link/QR can now upload, no account.", "pre-approved": "Only guests the host invited ahead of time can upload now.", "register-approve": "Guests can request access; uploads count once the host approves them." },
    visibility: { all: "Invitees now see every upload.", curated: "Invitees now see only the curated best-of subset." },
  };
  toast(messages[axis][value]);
  renderEvents();
}
function toggleTv() {
  const ev = DB.events[0];
  ev.axes.tv = !ev.axes.tv;
  toast(ev.axes.tv ? "TV wall is now live." : "TV wall turned off.");
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
      ${p.curated ? '<span class="chip curated">Curated</span>' : ""}
      <span class="fname">${p.filename}</span>
    </div>`).join("");
}
function toggleCurated(photoId) {
  const p = DB.photos.find((x) => x.id === photoId);
  p.curated = !p.curated;
  toast(`${p.filename} ${p.curated ? "added to" : "removed from"} the curated set.`);
  renderEvents();
}

// ---------------------------------------------------------- guest upload

let guestSelectedPool = new Set();
function openGuestUpload() {
  document.getElementById("guestUploadScreen").classList.remove("hidden");
  renderGuestUpload();
}
function closeGuestUpload() { document.getElementById("guestUploadScreen").classList.add("hidden"); }
function renderGuestUpload() {
  const ev = DB.events[0];
  const body = document.getElementById("guestUploadBody");
  if (ev.axes.uploadAccess === "pre-approved") {
    body.innerHTML = `<h2>${ev.name}</h2><p>This event only accepts uploads from people the host invited ahead of time. Ask ${userName(ev.hostUserId)} for an invite.</p>`;
    return;
  }
  if (ev.axes.uploadAccess === "register-approve") {
    body.innerHTML = `<h2>${ev.name}</h2>
      <p>Sign up to request upload access — the host approves each registrant before uploads count.</p>
      <div class="mock-field"><label>Your name</label><input type="text" placeholder="Guest name"></div>
      <div class="row"><button class="btn primary" onclick="document.getElementById('guestUploadBody').innerHTML='<h2>' + ${JSON.stringify(ev.name)}.replace(/'/g, \"\\\\'\") + '</h2><p>Request sent — your uploads will appear once ' + ${JSON.stringify(userName(ev.hostUserId))} + ' approves you.</p>'">Request access</button></div>`;
    return;
  }
  // free-for-all
  guestSelectedPool = new Set();
  body.innerHTML = `<h2>${ev.name}</h2>
    <p class="hint">No account needed. Photos you upload here are owned by the event's own account (${DB.users[ev.accountId].username}), never by you as an anonymous guest — see EVENTS.md's resolved ownership decision.</p>
    <div class="mock-field"><label>Choose files</label><div class="file-pool" id="guestFilePool"></div></div>
    <div class="row"><button class="btn primary" id="guestUploadBtn" disabled onclick="doGuestUpload()">Upload (<span id="guestSelectedCount">0</span> selected)</button></div>
    <div class="status-msg" id="guestUploadStatus"></div>`;
  renderGuestPool();
}
function renderGuestPool() {
  const poolEl = document.getElementById("guestFilePool");
  if (!pool.length) {
    poolEl.innerHTML = '<p class="empty-note">No more stock photos this session.</p>';
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
  document.getElementById("guestUploadStatus").innerHTML = `Uploaded ${count} photo${count === 1 ? "" : "s"}, owned by <b>${DB.users[ev.accountId].username}</b> (the event account) — not by you.`;
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
