// Endast klientsidan. Allt här är en fejkad databas i minnet som riktiga
// klick faktiskt förändrar — ingen server, inget lämnar den här sidan. Se
// documentation/tags/ (TAXONOMY.md, SCHEMA.md, UX_FLOWS.md) för designen
// detta illustrerar. Två medvetna mockup-förenklingar av schemat, för att
// göra grafen renderbar utan en riktig backend:
//   1. En relationstagg har HÄR två explicita referensrader (role:'subject'/
//      'object') istället för schemats enda "tag being qualified"-referens —
//      SCHEMA.md tillåter uttryckligen fler referensrader per tagg (se
//      co-presence-exemplet där), så detta är en tillämpning av den regeln,
//      inte en avvikelse från den.
//   2. Sökningens grafvandring görs mot `entities`, inte enskilda tagg-ID:n,
//      eftersom TAXONOMY.md är explicit om att det är entiteten sökningen
//      ska matcha mot (samma hund i tio bilder = samma sökbara sak).

function icon(name) { return `<span class="material-symbols-outlined">${name}</span>`; }
function escapeHtml(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// ---------------------------------------------------------------- taxonomy

const ENTITY_CATEGORIES = ["people", "objects", "animals", "places"];
const CATEGORIES = {
  origin:      { label: "Ursprung",            icon: "event",           desc: "Varifrån bilden kom: ett event, ett bröllop, en mapp, en uppladdningsomgång." },
  people:      { label: "Personer",            icon: "person",          desc: "Vem som är med på bilden, registrerad eller inte." },
  quality:     { label: "Kvalitet",             icon: "blur_on",         desc: "Suddig, svartvit, lågupplöst fickbild." },
  objects:     { label: "Föremål",              icon: "inventory_2",     desc: "En återkommande sak — en motorcykel, en båt, ett hus." },
  animals:     { label: "Djur",                 icon: "pets",            desc: "Ett återkommande husdjur — art, ras, namn." },
  places:      { label: "Platser",              icon: "place",           desc: "Allmän (en solig strand) eller specifik (hemma, en namngiven bil)." },
  privacy:     { label: "Sekretess",            icon: "lock",            desc: "Begränsar exponering — kan tvinga en tagg till privat, oavsett bildens delningsvillkor." },
  relationship:{ label: "Relationer",           icon: "link",            desc: "Länkar två andra taggar (\"min far\", i förhållande till hans hundtagg)." },
  activity:    { label: "Aktivitet/tillfälle",  icon: "celebration",     desc: "Vad som händer — skidåkning, ett kalas." },
  story:       { label: "Berättelse/narrativ",  icon: "auto_stories",    desc: "En bildtextstråd över flera bilder/taggar." },
  temporal:    { label: "Tid/säsong",           icon: "calendar_month",  desc: "Helg, årstid, tid på dygnet — mänskliga termer, inte rå EXIF-data." },
  co_presence: { label: "Samvaro/grupp",        icon: "groups",          desc: "\"De här personerna var tillsammans\" — en grupp, inte en person." },
};
const CATEGORY_ORDER = ["origin", "people", "animals", "objects", "places", "relationship", "co_presence", "story", "activity", "temporal", "quality", "privacy"];
const KIND_TO_CATEGORY = { person: "people", animal: "animals", object: "objects" };
const KIND_ICON = { person: "person", animal: "pets", object: "inventory_2" };
const KIND_QUESTION = { person: "Vem är detta?", animal: "Vilket djur?", object: "Vilket föremål?" };

// ---------------------------------------------------------------- seed data

const DB = { entities: {}, tags: [], tagReferences: [], photos: [] };
let seq = { entity: 1, tag: 1, ref: 1, photo: 1, box: 1 };
const nid = (kind) => kind[0] + seq[kind]++;

function mkEntity(type, displayName, attributes, linkedAccountUserId) {
  const id = nid("entity");
  DB.entities[id] = { id, type, displayName, attributes: attributes || {}, linkedAccountUserId: linkedAccountUserId || null };
  return DB.entities[id];
}
function mkPhoto(label, emoji, color, boxSpecs) {
  const id = nid("photo");
  const boxes = (boxSpecs || []).map((b) => ({ id: nid("box"), kind: b.kind, bbox: b.bbox, tagId: null }));
  const photo = { id, label, emoji, color, boxes };
  DB.photos.push(photo);
  return photo;
}
function addTag(photoId, category, text, opts) {
  opts = opts || {};
  const tag = { id: nid("tag"), photoId, userId: "joakim", tag: text, category, visibility: opts.visibility || "private", createdAt: Date.now() };
  DB.tags.push(tag);
  return tag;
}
function addRef(tagId, kind, value, extra) {
  extra = extra || {};
  const ref = { id: nid("ref"), tagId, referenceKind: kind, referenceValue: value, boundingBox: extra.boundingBox || null, role: extra.role || null };
  DB.tagReferences.push(ref);
  return ref;
}
function tagOnBox(photo, boxIndex, tag) { photo.boxes[boxIndex].tagId = tag.id; }

const eDad = mkEntity("person", "Pappa", {}, null);
const eAnna = mkEntity("person", "Anna", {}, "acc-anna");
const eErik = mkEntity("person", "Erik", {}, null);
const eSara = mkEntity("person", "Sara", {}, null);
const eBella = mkEntity("animal", "Bella", { species: "Hund", breed: "Labrador" }, null);
const eMoto = mkEntity("object", "Motorcykeln", { objectType: "Motorcykel" }, null);
const ePark = mkEntity("place", "Björkparken", { placeKind: "specific" }, null);
const eHome = mkEntity("place", "Hemma", { placeKind: "specific" }, null);

// p1 — grillkväll: Pappa, Anna, Bella tillsammans + relationen Pappa äger Bella
const p1 = mkPhoto("Grillkväll hemma", "🍢", "#3a5a7a", [
  { kind: "person", bbox: [6, 16, 26, 62] },
  { kind: "person", bbox: [40, 12, 26, 66] },
  { kind: "animal", bbox: [70, 46, 25, 42] },
]);
addTag(p1.id, "origin", "Sommaren 2019", { visibility: "shareable" });
addTag(p1.id, "temporal", "Sommar", { visibility: "shareable" });
addTag(p1.id, "activity", "Grillkväll", { visibility: "shareable" });
const tDadP1 = addTag(p1.id, "people", "Pappa", { visibility: "private" });
addRef(tDadP1.id, "entity", eDad.id, { boundingBox: p1.boxes[0].bbox }); tagOnBox(p1, 0, tDadP1);
const tAnnaP1 = addTag(p1.id, "people", "Anna", { visibility: "shareable" });
addRef(tAnnaP1.id, "entity", eAnna.id, { boundingBox: p1.boxes[1].bbox }); tagOnBox(p1, 1, tAnnaP1);
const tBellaP1 = addTag(p1.id, "animals", "Bella", { visibility: "shareable" });
addRef(tBellaP1.id, "entity", eBella.id, { boundingBox: p1.boxes[2].bbox }); tagOnBox(p1, 2, tBellaP1);
const relDadBella = addTag(p1.id, "relationship", "ägare av", { visibility: "private" });
addRef(relDadBella.id, "tag", tDadP1.id, { role: "subject" });
addRef(relDadBella.id, "tag", tBellaP1.id, { role: "object" });

// p2 — Bella ensam (ingen Pappa i bild) — visar att entiteten hittas ändå
const p2 = mkPhoto("Bella på gräsmattan", "🐕", "#3a6a4a", [{ kind: "animal", bbox: [28, 28, 46, 58] }]);
const tBellaP2 = addTag(p2.id, "animals", "Bella", { visibility: "shareable" });
addRef(tBellaP2.id, "entity", eBella.id, { boundingBox: p2.boxes[0].bbox }); tagOnBox(p2, 0, tBellaP2);
addTag(p2.id, "temporal", "Höst", { visibility: "shareable" });

// p3 — Pappas motorcykel (Pappa syns inte här heller)
const p3 = mkPhoto("Pappas motorcykel i garaget", "🏍️", "#4a4a52", [{ kind: "object", bbox: [14, 24, 72, 62] }]);
const tMotoP3 = addTag(p3.id, "objects", "Motorcykeln", { visibility: "private" });
addRef(tMotoP3.id, "entity", eMoto.id, { boundingBox: p3.boxes[0].bbox }); tagOnBox(p3, 0, tMotoP3);
const relDadMoto = addTag(p3.id, "relationship", "ägare av", { visibility: "private" });
addRef(relDadMoto.id, "tag", tDadP1.id, { role: "subject" });
addRef(relDadMoto.id, "tag", tMotoP3.id, { role: "object" });

// p4/p5 — Annas 30-årskalas: berättelsetråd + samvarotagg ("Kalasgänget")
const p4 = mkPhoto("Annas 30-årskalas — tårtan", "🎂", "#6a3a6a", [
  { kind: "person", bbox: [8, 18, 24, 62] },
  { kind: "person", bbox: [38, 16, 24, 64] },
  { kind: "person", bbox: [66, 20, 24, 60] },
]);
const tAnnaP4 = addTag(p4.id, "people", "Anna", { visibility: "shareable" });
addRef(tAnnaP4.id, "entity", eAnna.id, { boundingBox: p4.boxes[0].bbox }); tagOnBox(p4, 0, tAnnaP4);
const tErikP4 = addTag(p4.id, "people", "Erik", { visibility: "shareable" });
addRef(tErikP4.id, "entity", eErik.id, { boundingBox: p4.boxes[1].bbox }); tagOnBox(p4, 1, tErikP4);
const tSaraP4 = addTag(p4.id, "people", "Sara", { visibility: "shareable" });
addRef(tSaraP4.id, "entity", eSara.id, { boundingBox: p4.boxes[2].bbox }); tagOnBox(p4, 2, tSaraP4);
addTag(p4.id, "activity", "Kalas", { visibility: "shareable" });
const storyRoot = addTag(p4.id, "story", "Annas 30-årskalas", { visibility: "shareable" });
const coTag = addTag(p4.id, "co_presence", "Kalasgänget", { visibility: "shareable" });
[eAnna, eErik, eSara, eDad].forEach((e) => addRef(coTag.id, "entity", e.id));

const p5 = mkPhoto("Annas 30-årskalas — dansgolvet", "🕺", "#6a3a4a", [
  { kind: "person", bbox: [18, 14, 26, 66] },
  { kind: "person", bbox: [52, 16, 26, 64] },
]);
const tAnnaP5 = addTag(p5.id, "people", "Anna", { visibility: "shareable" });
addRef(tAnnaP5.id, "entity", eAnna.id, { boundingBox: p5.boxes[0].bbox }); tagOnBox(p5, 0, tAnnaP5);
const tErikP5 = addTag(p5.id, "people", "Erik", { visibility: "shareable" });
addRef(tErikP5.id, "entity", eErik.id, { boundingBox: p5.boxes[1].bbox }); tagOnBox(p5, 1, tErikP5);
addTag(p5.id, "activity", "Kalas", { visibility: "shareable" });
const storyJoin = addTag(p5.id, "story", "Annas 30-årskalas", { visibility: "shareable" });
addRef(storyJoin.id, "tag", storyRoot.id, { role: "story_thread" });

// p6 — kvalitetskategorin
const p6 = mkPhoto("Suddig bild från fickan", "📱", "#4a4a4a", []);
addTag(p6.id, "quality", "Oskarp", { visibility: "private" });

// p7 — sekretesskategorin: tvingar privat, oavsett att origin-taggen är delningsbar
const p7 = mkPhoto("Foto av legitimation", "🪪", "#2a2a2e", []);
addTag(p7.id, "privacy", "Skyddat (känsligt dokument)", { visibility: "private" });
addTag(p7.id, "origin", "Sommaren 2019", { visibility: "shareable" });

// p8 — plats kopplad till Bella ("favoritplats för") — 1 hopp från Pappa via Bella
const p8 = mkPhoto("Bella i Björkparken", "🌳", "#2a5a3a", [{ kind: "animal", bbox: [34, 34, 42, 52] }]);
const tBellaP8 = addTag(p8.id, "animals", "Bella", { visibility: "shareable" });
addRef(tBellaP8.id, "entity", eBella.id, { boundingBox: p8.boxes[0].bbox }); tagOnBox(p8, 0, tBellaP8);
const tParkP8 = addTag(p8.id, "places", "Björkparken", { visibility: "shareable" });
addRef(tParkP8.id, "entity", ePark.id);
const relParkBella = addTag(p8.id, "relationship", "favoritplats för", { visibility: "shareable" });
addRef(relParkBella.id, "tag", tParkP8.id, { role: "subject" });
addRef(relParkBella.id, "tag", tBellaP8.id, { role: "object" });

// p9 — Hemma kopplat till Pappa ("hem för") — ytterligare 1-hoppsexempel
const p9 = mkPhoto("Hemma i trädgården", "🏡", "#5a4a2a", []);
const tHomeP9 = addTag(p9.id, "places", "Hemma", { visibility: "shareable" });
addRef(tHomeP9.id, "entity", eHome.id);
const relHomeDad = addTag(p9.id, "relationship", "hem för", { visibility: "shareable" });
addRef(relHomeDad.id, "tag", tHomeP9.id, { role: "subject" });
addRef(relHomeDad.id, "tag", tDadP1.id, { role: "object" });

// p10 — samma platsentitet (Björkparken) som p8, men ingen egen relationskant
// härifrån — hittas ändå 2 hopp ut från "Pappa" (Pappa→Bella→Björkparken),
// precis som TAXONOMY.md:s exempel "hans hunds bilder ... även där han inte
// själv syns" beskriver.
const p10 = mkPhoto("Björkparken på vintern", "❄️", "#3a4a5a", []);
const tParkP10 = addTag(p10.id, "places", "Björkparken", { visibility: "shareable" });
addRef(tParkP10.id, "entity", ePark.id);

// -------------------------------------------------------------------- state

let currentTab = "gallery";
let openPhotoId = null;
let galleryCategoryFilter = null;
let addTagCtx = null;
let searchMaxHops = 2;
let lastSearchQuery = "";

// ---------------------------------------------------------------- toasts

let toastTimer = null;
function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.add("hidden"), 3400);
}

// ------------------------------------------------------------------ tabs

function switchTab(name) {
  currentTab = name;
  document.querySelectorAll("#tabNav .nav-pill").forEach((b) => b.classList.toggle("current", b.dataset.tab === name));
  document.querySelectorAll(".tab-panel").forEach((p) => p.classList.toggle("hidden", p.id !== "tab-" + name));
  render();
}

function render() {
  if (currentTab === "gallery") renderGallery();
  if (currentTab === "search") renderSearchTab();
  if (currentTab === "categories") renderCategoryLegend();
  if (openPhotoId) renderPhotoDetail(openPhotoId);
}

// --------------------------------------------------------------- helpers

function photoTags(photoId) { return DB.tags.filter((t) => t.photoId === photoId); }
function tagEntity(tagId) {
  const ref = DB.tagReferences.find((r) => r.tagId === tagId && r.referenceKind === "entity");
  return ref ? DB.entities[ref.referenceValue] : null;
}
function photoHasPrivacyTag(photoId) { return photoTags(photoId).some((t) => t.category === "privacy"); }
function entityBadge(entity, compact) {
  if (!entity || entity.type !== "person") return "";
  const label = entity.linkedAccountUserId ? "Kopplat konto" : "Lokal";
  const cls = entity.linkedAccountUserId ? "linked" : "local";
  const ic = entity.linkedAccountUserId ? "verified" : "person";
  return `<span class="entity-badge ${cls}" title="${label}">${icon(ic)}${compact ? "" : label}</span>`;
}

// -------------------------------------------------------------- gallery

function thumbHtml(photo) {
  const count = photoTags(photo.id).length;
  const lock = photoHasPrivacyTag(photo.id) ? icon("lock") + " " : "";
  return `<div class="thumb" style="background:${photo.color}" onclick="openPhotoDetail('${photo.id}')">
    <span class="emoji">${photo.emoji}</span>
    <span class="tagcount">${lock}${count} tagg${count === 1 ? "" : "ar"}</span>
    <span class="fname">${escapeHtml(photo.label)}</span>
  </div>`;
}

function renderGallery() {
  const filterRow = document.getElementById("galleryFilterRow");
  filterRow.innerHTML = galleryCategoryFilter
    ? `<button class="chip-choice selected" onclick="clearGalleryFilter()">${icon(CATEGORIES[galleryCategoryFilter].icon)}${CATEGORIES[galleryCategoryFilter].label} ${icon("close")}</button>`
    : "";
  const list = galleryCategoryFilter
    ? DB.photos.filter((p) => photoTags(p.id).some((t) => t.category === galleryCategoryFilter))
    : DB.photos;
  document.getElementById("galleryGrid").innerHTML = list.map(thumbHtml).join("");
}
function clearGalleryFilter() { galleryCategoryFilter = null; renderGallery(); }
function filterGalleryByCategory(key) {
  galleryCategoryFilter = key;
  switchTab("gallery");
}

// ---------------------------------------------------------- category tab

function renderCategoryLegend() {
  document.getElementById("categoryLegend").innerHTML = CATEGORY_ORDER.map((key) => {
    const c = CATEGORIES[key];
    const n = DB.photos.filter((p) => photoTags(p.id).some((t) => t.category === key)).length;
    return `<button class="cat-card" onclick="filterGalleryByCategory('${key}')">
      <div class="cat-title">${icon(c.icon)}${c.label}</div>
      <p class="cat-desc">${c.desc}</p>
      <div class="cat-meta">${n} bild${n === 1 ? "" : "er"} taggade &middot; visa i galleriet</div>
    </button>`;
  }).join("");
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
  renderGallery();
}

function boxHtml(photo, box) {
  const style = `left:${box.bbox[0]}%; top:${box.bbox[1]}%; width:${box.bbox[2]}%; height:${box.bbox[3]}%;`;
  if (box.tagId) {
    const entity = tagEntity(box.tagId);
    return `<div class="bbox tagged" style="${style}" onclick="onTaggedBoxClick('${box.tagId}')" title="Redan taggad — se tagglistan nedan för att ändra">
      <span class="bbox-label">${icon(KIND_ICON[box.kind])}${escapeHtml(entity.displayName)} ${entityBadge(entity, true)}</span>
    </div>`;
  }
  return `<div class="bbox bbox-untagged" style="${style}" onclick="openAddTagForBox('${photo.id}','${box.id}')">
    <span class="bbox-label">${icon(KIND_ICON[box.kind])}${KIND_QUESTION[box.kind]}</span>
  </div>`;
}
function onTaggedBoxClick(tagId) {
  const tag = DB.tags.find((t) => t.id === tagId);
  const entity = tagEntity(tagId);
  toast(`Redan taggad som "${entity ? entity.displayName : tag.tag}" — justera synlighet eller ta bort i tagglistan nedan.`);
}

function tagItemHtml(tag) {
  const c = CATEGORIES[tag.category];
  const entity = tagEntity(tag.id);
  let chain = "";
  if (tag.category === "relationship") {
    const refs = DB.tagReferences.filter((r) => r.tagId === tag.id);
    const subj = refs.find((r) => r.role === "subject");
    const obj = refs.find((r) => r.role === "object");
    const subjTag = subj && DB.tags.find((t) => t.id === subj.referenceValue);
    const objTag = obj && DB.tags.find((t) => t.id === obj.referenceValue);
    if (subjTag && objTag) chain = `<div class="tag-chain">${icon("link")}${escapeHtml(subjTag.tag)} —(${escapeHtml(tag.tag)})→ ${escapeHtml(objTag.tag)}</div>`;
  } else if (tag.category === "co_presence") {
    const names = DB.tagReferences.filter((r) => r.tagId === tag.id && r.referenceKind === "entity").map((r) => DB.entities[r.referenceValue].displayName);
    chain = `<div class="tag-chain">${icon("groups")}${names.map(escapeHtml).join(", ")}</div>`;
  } else if (tag.category === "story") {
    const joinRef = DB.tagReferences.find((r) => r.tagId === tag.id && r.referenceKind === "tag");
    if (joinRef) {
      const root = DB.tags.find((t) => t.id === joinRef.referenceValue);
      const rootPhoto = DB.photos.find((p) => p.id === root.photoId);
      chain = `<div class="tag-chain">${icon("auto_stories")}Ansluter till samma berättelse som "${escapeHtml(rootPhoto.label)}"</div>`;
    } else {
      const joiners = DB.tagReferences.filter((r) => r.referenceKind === "tag" && r.referenceValue === tag.id);
      if (joiners.length) chain = `<div class="tag-chain">${icon("auto_stories")}${joiners.length} till bild ansluter till den här berättelsen</div>`;
    }
  }
  const isPrivacyForced = tag.category === "privacy";
  const pressed = tag.visibility === "shareable";
  return `<div class="tag-item">
    <div class="tag-head">
      <div class="tag-main">
        <span class="tag-cat-icon">${icon(c.icon)}</span>
        <span class="category-tag-label">${c.label}</span>
        <span class="tag-text">${escapeHtml(tag.tag)}</span>
        ${entityBadge(entity)}
      </div>
      <div class="tag-vis">
        ${isPrivacyForced ? `${icon("lock")}alltid privat` : (tag.visibility === "shareable" ? `${icon("public")}delningsbar` : `${icon("lock")}privat`)}
        <button class="toggle" aria-pressed="${pressed}" ${isPrivacyForced ? "disabled" : ""} onclick="toggleTagVisibility('${tag.id}')"></button>
      </div>
    </div>
    ${chain}
    <div class="tag-actions">
      <button class="btn small ghost" onclick="openShareTagAlbum('${tag.category}', '${encodeURIComponent(tag.tag)}')">${icon("share")}Dela som album</button>
      <button class="btn small ghost" onclick="removeTag('${tag.id}')">${icon("delete")}Ta bort</button>
    </div>
  </div>`;
}

function renderPhotoDetail(photoId) {
  const photo = DB.photos.find((p) => p.id === photoId);
  if (!photo) return;
  const tags = photoTags(photo.id);
  const groups = CATEGORY_ORDER.map((key) => ({ key, tags: tags.filter((t) => t.category === key) })).filter((g) => g.tags.length);
  const lockNote = photoHasPrivacyTag(photo.id)
    ? `<div class="photo-stage-lock-note">${icon("lock")}<span>Den här bilden bär en sekretesstagg — den visas normalt för dig som ägare, men hålls automatiskt utanför alla delade album (se tagglistan nedan).</span></div>`
    : "";
  document.getElementById("photoDetailBody").innerHTML = `
    <button class="lb-btn lb-close" onclick="closePhotoDetail()">${icon("close")}</button>
    <div class="photo-stage" style="background:${photo.color}">
      ${photo.emoji}
      ${photo.boxes.map((b) => boxHtml(photo, b)).join("")}
      ${lockNote}
    </div>
    <h2>${escapeHtml(photo.label)}</h2>
    ${groups.map((g) => `<h3>${icon(CATEGORIES[g.key].icon)}${CATEGORIES[g.key].label}</h3>${g.tags.map(tagItemHtml).join("")}`).join("")}
    <div class="row" style="margin-top:1.2rem;">
      <button class="btn primary" onclick="openAddTagPicker('${photo.id}')">${icon("add")}Lägg till tagg</button>
    </div>
  `;
}

function toggleTagVisibility(tagId) {
  const tag = DB.tags.find((t) => t.id === tagId);
  if (tag.category === "privacy") return;
  tag.visibility = tag.visibility === "private" ? "shareable" : "private";
  renderPhotoDetail(openPhotoId);
}
function removeTag(tagId) {
  const idx = DB.tags.findIndex((t) => t.id === tagId);
  if (idx === -1) return;
  const [removed] = DB.tags.splice(idx, 1);
  // kaskad: relations-/berättelsetaggar som pekade på den borttagna taggen blir hängande — ta bort dem också
  const dependents = DB.tags.filter((t) => DB.tagReferences.some((r) => r.tagId === t.id && r.referenceKind === "tag" && r.referenceValue === tagId));
  dependents.forEach((d) => removeTag(d.id));
  DB.tagReferences = DB.tagReferences.filter((r) => r.tagId !== tagId && r.referenceValue !== tagId);
  DB.photos.forEach((p) => p.boxes.forEach((b) => { if (b.tagId === tagId) b.tagId = null; }));
  toast(`Tog bort taggen "${removed.tag}".`);
  renderPhotoDetail(openPhotoId);
  renderGallery();
}

// ------------------------------------------------------------- add tag UI

function openAddTagPicker(photoId) {
  addTagCtx = { photoId, boxId: null };
  document.getElementById("addTagModalBody").innerHTML = `
    <button class="lb-btn lb-close" onclick="closeAddTagModal()">${icon("close")}</button>
    <h2>${icon("sell")}Lägg till tagg</h2>
    <p class="section-sub small">Alla 12 kategorier från taxonomin — välj en för att se dess taggningsflöde.</p>
    <div class="picker-grid">
      ${CATEGORY_ORDER.map((key) => `<button class="picker-tile" onclick="openAddTagForm('${photoId}', null, '${key}')">
        <div class="pt-title">${icon(CATEGORIES[key].icon)}${CATEGORIES[key].label}</div>
        <p class="pt-desc">${CATEGORIES[key].desc}</p>
      </button>`).join("")}
    </div>
  `;
  document.getElementById("addTagModal").classList.remove("hidden");
}
function openAddTagForBox(photoId, boxId) {
  const photo = DB.photos.find((p) => p.id === photoId);
  const box = photo.boxes.find((b) => b.id === boxId);
  openAddTagForm(photoId, boxId, KIND_TO_CATEGORY[box.kind]);
}
function closeAddTagModal() {
  document.getElementById("addTagModal").classList.add("hidden");
  addTagCtx = null;
  renderPhotoDetail(openPhotoId);
}

function visSegHtml(id, dflt) {
  return `<div class="mock-field"><label>Synlighet</label><div class="seg" id="${id}">
    <button data-v="private" aria-pressed="${dflt !== "shareable"}" onclick="setSegVal(this)">${icon("lock")}Privat</button>
    <button data-v="shareable" aria-pressed="${dflt === "shareable"}" onclick="setSegVal(this)">${icon("public")}Delningsbar</button>
  </div></div>`;
}
function setSegVal(btn) {
  btn.parentElement.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", "false"));
  btn.setAttribute("aria-pressed", "true");
}
function segVal(id) { return document.querySelector(`#${id} button[aria-pressed="true"]`).dataset.v; }

function openAddTagForm(photoId, boxId, category) {
  addTagCtx = { photoId, boxId, category };
  const body = document.getElementById("addTagModalBody");
  const c = CATEGORIES[category];
  const back = boxId ? "" : `<button class="btn small ghost" onclick="openAddTagPicker('${photoId}')">${icon("arrow_back")}Alla kategorier</button>`;
  const header = `<button class="lb-btn lb-close" onclick="closeAddTagModal()">${icon("close")}</button>
    <h2>${icon(c.icon)}${c.label}</h2>
    <p class="section-sub small">${c.desc}</p>${back}<div id="addTagFormBody"></div>`;
  body.innerHTML = header;
  const formEl = document.getElementById("addTagFormBody");

  if (category === "origin" || category === "activity" || category === "temporal" || category === "quality" || category === "story") {
    formEl.innerHTML = renderSimpleForm(category);
  } else if (category === "people") {
    formEl.innerHTML = renderPeopleForm();
  } else if (category === "animals") {
    formEl.innerHTML = renderAnimalForm();
  } else if (category === "objects") {
    formEl.innerHTML = renderObjectForm();
  } else if (category === "places") {
    formEl.innerHTML = renderPlaceForm();
  } else if (category === "privacy") {
    formEl.innerHTML = renderPrivacyForm();
  } else if (category === "relationship") {
    formEl.innerHTML = renderRelationshipForm(photoId);
  } else if (category === "co_presence") {
    formEl.innerHTML = renderCoPresenceForm();
  }
  document.getElementById("addTagModal").classList.remove("hidden");
}

const PRESETS = {
  activity: ["Kalas", "Skidåkning", "Fotbollsmatch", "Grillkväll"],
  temporal: ["Sommar", "Höst", "Vinter", "Vår", "Jul", "Midsommar", "Kväll", "Morgon"],
  quality: ["Oskarp", "Svartvit", "Lågupplöst/fickfoto"],
};

function renderSimpleForm(category) {
  if (category === "story") {
    const roots = DB.tags.filter((t) => t.category === "story" && !DB.tagReferences.some((r) => r.tagId === t.id && r.referenceKind === "tag"));
    return `
      <div class="mock-field"><label>Starta en ny berättelse</label><input type="text" id="newFieldText" placeholder="t.ex. Sommarens roadtrip"></div>
      ${visSegHtml("visSeg", "shareable")}
      <div class="row"><button class="btn primary" onclick="submitSimpleTag('story')">${icon("add")}Starta berättelse</button></div>
      ${roots.length ? `<h3 style="margin-top:1.2rem;">${icon("auto_stories")}...eller anslut till en befintlig</h3>
        <div class="picker-grid">${roots.map((r) => `<button class="picker-tile" onclick="joinStory('${r.id}')"><div class="pt-title">${escapeHtml(r.tag)}</div></button>`).join("")}</div>` : ""}
    `;
  }
  const presets = PRESETS[category];
  return `
    ${presets ? `<div class="mock-field"><label>Snabbval</label><div>${presets.map((p) => `<button class="chip-choice" onclick="document.getElementById('newFieldText').value='${p}'">${escapeHtml(p)}</button>`).join("")}</div></div>` : ""}
    <div class="mock-field"><label>Text</label><input type="text" id="newFieldText" placeholder="Egen text"></div>
    ${visSegHtml("visSeg", "shareable")}
    <div class="row"><button class="btn primary" onclick="submitSimpleTag('${category}')">${icon("add")}Lägg till</button></div>
  `;
}
function submitSimpleTag(category) {
  const text = document.getElementById("newFieldText").value.trim();
  if (!text) { toast("Skriv en text först."); return; }
  const tag = addTag(addTagCtx.photoId, category, text, { visibility: segVal("visSeg") });
  toast(`Lade till "${text}" (${CATEGORIES[category].label}).`);
  closeAddTagModal();
}
function joinStory(rootId) {
  const root = DB.tags.find((t) => t.id === rootId);
  const tag = addTag(addTagCtx.photoId, "story", root.tag, { visibility: root.visibility });
  addRef(tag.id, "tag", rootId, { role: "story_thread" });
  toast(`Ansluten till berättelsen "${root.tag}".`);
  closeAddTagModal();
}

function renderPeopleForm() {
  return `
    <div class="mock-field"><label>Vem är detta? — börja skriv för att matcha tidigare personer</label>
      <input type="text" id="personSearch" placeholder="t.ex. da..." oninput="renderPersonAutocomplete()">
      <ul class="autocomplete-list" id="personAutocomplete"></ul>
    </div>
    <p class="hint">Ingen träff? Skapa en ny lokal person (synlig bara för dig, inte kopplad till något konto):</p>
    <div class="mock-field"><label>Namn</label><input type="text" id="newPersonName" placeholder="Namn"></div>
    <div class="row"><button class="btn ghost" onclick="createLocalPersonAndTag()">${icon("person_add")}Skapa ny lokal person</button></div>
  `;
}
function renderPersonAutocomplete() {
  const q = document.getElementById("personSearch").value.trim().toLowerCase();
  const list = document.getElementById("personAutocomplete");
  if (!q) { list.innerHTML = ""; return; }
  const matches = Object.values(DB.entities).filter((e) => e.type === "person" && e.displayName.toLowerCase().includes(q));
  list.innerHTML = matches.length
    ? matches.map((e) => `<li onclick="confirmPersonTag('${e.id}')">${entityBadge(e)}${escapeHtml(e.displayName)}</li>`).join("")
    : `<li style="opacity:0.6; cursor:default;">Ingen tidigare person matchar — skapa ny nedan.</li>`;
}
function createLocalPersonAndTag() {
  const name = document.getElementById("newPersonName").value.trim();
  if (!name) { toast("Skriv ett namn först."); return; }
  const entity = mkEntity("person", name, {}, null);
  confirmPersonTag(entity.id);
}
function confirmPersonTag(entityId) {
  const entity = DB.entities[entityId];
  const ctx = addTagCtx;
  const tag = addTag(ctx.photoId, "people", entity.displayName, { visibility: "private" });
  addRef(tag.id, "entity", entityId, ctx.boxId ? { boundingBox: DB.photos.find((p) => p.id === ctx.photoId).boxes.find((b) => b.id === ctx.boxId).bbox } : {});
  if (ctx.boxId) { const photo = DB.photos.find((p) => p.id === ctx.photoId); const box = photo.boxes.find((b) => b.id === ctx.boxId); box.tagId = tag.id; }
  if (!entity.linkedAccountUserId) {
    renderInviteCta(entity);
  } else {
    toast(`Taggade "${entity.displayName}" (kopplat konto).`);
    closeAddTagModal();
  }
}
function renderInviteCta(entity) {
  document.getElementById("addTagFormBody").innerHTML = `
    <div class="callout info">
      <span class="label">${entity.displayName} är inte kopplad till något DPFAS-konto</span>
      <p>Taggen sparas som en lokal, privat post tills vidare. Du kan bjuda in henne, eller dela taggen/albumet direkt — se UX_FLOWS.md:s "invite CTA".</p>
    </div>
    <div class="row">
      <button class="btn primary" onclick="sendInvite('${entity.id}')">${icon("mail")}Skicka inbjudningslänk</button>
      <button class="btn ghost" onclick="closeAddTagModal(); toast('Öppna Dela-knappen i tagglistan för att dela med ${escapeHtml(entity.displayName)} direkt.');">${icon("share")}Dela taggen med henne istället</button>
      <button class="btn ghost" onclick="closeAddTagModal()">${icon("close")}Hoppa över</button>
    </div>
  `;
}
function sendInvite(entityId) {
  const entity = DB.entities[entityId];
  toast(`(mock) Inbjudningslänk skickad för ${entity.displayName}. Kontot förblir lokalt tills hon registrerar sig.`);
  closeAddTagModal();
}

function renderAnimalForm() {
  const owners = Object.values(DB.entities).filter((e) => e.type === "person");
  return `
    <div class="mock-field"><label>Namn</label><input type="text" id="animalName" placeholder="t.ex. Bella"></div>
    <div class="mock-field"><label>Art</label><input type="text" id="animalType" placeholder="t.ex. Hund"></div>
    <div class="mock-field"><label>Ras</label><input type="text" id="animalBreed" placeholder="t.ex. Labrador"></div>
    <div class="mock-field"><label>Länka ägare (valfritt — skapar en relationstagg)</label>
      <select id="animalOwner"><option value="">— ingen —</option>${owners.map((o) => `<option value="${o.id}">${escapeHtml(o.displayName)}</option>`).join("")}</select>
    </div>
    ${visSegHtml("visSeg", "shareable")}
    <div class="row"><button class="btn primary" onclick="submitAnimalTag()">${icon("add")}Lägg till djurtagg</button></div>
  `;
}
function canonicalTagForEntity(entityId) {
  const ref = DB.tagReferences.find((r) => r.referenceKind === "entity" && r.referenceValue === entityId);
  return ref ? DB.tags.find((t) => t.id === ref.tagId) : null;
}
function submitAnimalTag() {
  const name = document.getElementById("animalName").value.trim();
  if (!name) { toast("Skriv ett namn först."); return; }
  const type = document.getElementById("animalType").value.trim() || "Djur";
  const breed = document.getElementById("animalBreed").value.trim();
  const ownerId = document.getElementById("animalOwner").value;
  const entity = mkEntity("animal", name, { species: type, breed }, null);
  const ctx = addTagCtx;
  const photo = DB.photos.find((p) => p.id === ctx.photoId);
  const box = ctx.boxId ? photo.boxes.find((b) => b.id === ctx.boxId) : null;
  const tag = addTag(ctx.photoId, "animals", name, { visibility: segVal("visSeg") });
  addRef(tag.id, "entity", entity.id, box ? { boundingBox: box.bbox } : {});
  if (box) box.tagId = tag.id;
  if (ownerId) {
    let ownerTag = canonicalTagForEntity(ownerId) || (() => {
      const t = addTag(ctx.photoId, "people", DB.entities[ownerId].displayName, { visibility: "private" });
      addRef(t.id, "entity", ownerId);
      return t;
    })();
    const rel = addTag(ctx.photoId, "relationship", "ägare av", { visibility: "private" });
    addRef(rel.id, "tag", ownerTag.id, { role: "subject" });
    addRef(rel.id, "tag", tag.id, { role: "object" });
  }
  toast(`Lade till djuret "${name}".`);
  closeAddTagModal();
}

function renderObjectForm() {
  return `
    <div class="mock-field"><label>Namn</label><input type="text" id="objectName" placeholder="t.ex. Segelbåten"></div>
    <div class="mock-field"><label>Typ</label><input type="text" id="objectType" placeholder="t.ex. Båt"></div>
    ${visSegHtml("visSeg", "shareable")}
    <div class="row"><button class="btn primary" onclick="submitObjectTag()">${icon("add")}Lägg till föremålstagg</button></div>
  `;
}
function submitObjectTag() {
  const name = document.getElementById("objectName").value.trim();
  if (!name) { toast("Skriv ett namn först."); return; }
  const type = document.getElementById("objectType").value.trim() || "Föremål";
  const entity = mkEntity("object", name, { objectType: type }, null);
  const ctx = addTagCtx;
  const photo = DB.photos.find((p) => p.id === ctx.photoId);
  const box = ctx.boxId ? photo.boxes.find((b) => b.id === ctx.boxId) : null;
  const tag = addTag(ctx.photoId, "objects", name, { visibility: segVal("visSeg") });
  addRef(tag.id, "entity", entity.id, box ? { boundingBox: box.bbox } : {});
  if (box) box.tagId = tag.id;
  toast(`Lade till föremålet "${name}".`);
  closeAddTagModal();
}

function renderPlaceForm() {
  return `
    <div class="mock-field"><label>Namn</label><input type="text" id="placeName" placeholder="t.ex. Sommarstugan"></div>
    <div class="mock-field"><label>Typ</label>
      <div class="seg" id="placeKindSeg">
        <button data-v="general" aria-pressed="true" onclick="setSegVal(this)">Allmän</button>
        <button data-v="specific" aria-pressed="false" onclick="setSegVal(this)">Specifik</button>
      </div>
    </div>
    ${visSegHtml("visSeg", "shareable")}
    <div class="row"><button class="btn primary" onclick="submitPlaceTag()">${icon("add")}Lägg till platstagg</button></div>
  `;
}
function submitPlaceTag() {
  const name = document.getElementById("placeName").value.trim();
  if (!name) { toast("Skriv ett namn först."); return; }
  const kind = segVal("placeKindSeg");
  const entity = mkEntity("place", name, { placeKind: kind }, null);
  const tag = addTag(addTagCtx.photoId, "places", name, { visibility: segVal("visSeg") });
  addRef(tag.id, "entity", entity.id);
  toast(`Lade till platsen "${name}".`);
  closeAddTagModal();
}

function renderPrivacyForm() {
  return `
    <p class="hint">Sekretesskategorin tvingar taggens synlighet till <b>privat</b> — det går inte att göra delningsbar, oavsett bildens egna delningsvillkor. Automatisk detektion (t.ex. nakenbilder) är inte byggd — se TODO.md; idag väljs detta manuellt.</p>
    <div class="mock-field"><label>Vad ska döljas?</label>
      <div class="seg" id="privacyPresetSeg">
        <button data-v="Skyddat (känsligt dokument)" aria-pressed="true" onclick="setSegVal(this)">Känsligt dokument</button>
        <button data-v="Skyddat (privat innehåll)" aria-pressed="false" onclick="setSegVal(this)">Annat privat innehåll</button>
      </div>
    </div>
    <div class="row"><button class="btn primary" onclick="submitPrivacyTag()">${icon("lock")}Gör alltid privat</button></div>
  `;
}
function submitPrivacyTag() {
  const val = segVal("privacyPresetSeg");
  addTag(addTagCtx.photoId, "privacy", val, { visibility: "private" });
  toast(`Bilden bär nu en sekretesstagg — utesluts automatiskt ur alla delade album.`);
  closeAddTagModal();
}

function renderRelationshipForm(photoId) {
  const all = DB.tags.filter((t) => t.category !== "relationship").map((t) => {
    const photo = DB.photos.find((p) => p.id === t.photoId);
    return { id: t.id, label: `${photo.label} — ${t.tag} (${CATEGORIES[t.category].label})` };
  });
  const opts = all.map((t) => `<option value="${t.id}">${escapeHtml(t.label)}</option>`).join("");
  return `
    <p class="hint">En relationstagg länkar två befintliga taggar, t.ex. "min far" i förhållande till hans hundtagg — geometrin (rutan) är alltid oberoende av vad den refererar till.</p>
    <div class="mock-field"><label>Utgår ifrån</label><select id="relSubject">${opts}</select></div>
    <div class="mock-field"><label>Relationsord</label><input type="text" id="relWord" placeholder="t.ex. vän med, ägare av, förälder till"></div>
    <div class="mock-field"><label>Pekar på</label><select id="relObject">${opts}</select></div>
    ${visSegHtml("visSeg", "private")}
    <div class="row"><button class="btn primary" onclick="submitRelationshipTag('${photoId}')">${icon("link")}Skapa relationstagg</button></div>
  `;
}
function submitRelationshipTag(photoId) {
  const subjId = document.getElementById("relSubject").value;
  const objId = document.getElementById("relObject").value;
  const word = document.getElementById("relWord").value.trim();
  if (!word) { toast("Skriv ett relationsord först."); return; }
  if (subjId === objId) { toast("Utgångstagg och måltagg kan inte vara samma."); return; }
  const rel = addTag(photoId, "relationship", word, { visibility: segVal("visSeg") });
  addRef(rel.id, "tag", subjId, { role: "subject" });
  addRef(rel.id, "tag", objId, { role: "object" });
  toast(`Skapade relationen "${word}".`);
  closeAddTagModal();
}

function renderCoPresenceForm() {
  const people = Object.values(DB.entities).filter((e) => e.type === "person");
  return `
    <div class="mock-field"><label>Vilka var tillsammans?</label>
      <div id="coPresenceChoices">${people.map((e) => `<button class="chip-choice" data-id="${e.id}" onclick="this.classList.toggle('selected')">${escapeHtml(e.displayName)}</button>`).join("")}</div>
    </div>
    <div class="mock-field"><label>Namn på gruppen</label><input type="text" id="coPresenceName" placeholder="t.ex. Kalasgänget"></div>
    ${visSegHtml("visSeg", "shareable")}
    <div class="row"><button class="btn primary" onclick="submitCoPresenceTag()">${icon("groups")}Skapa gruppagg</button></div>
  `;
}
function submitCoPresenceTag() {
  const name = document.getElementById("coPresenceName").value.trim();
  const selected = [...document.querySelectorAll("#coPresenceChoices .chip-choice.selected")].map((b) => b.dataset.id);
  if (!name) { toast("Ge gruppen ett namn först."); return; }
  if (selected.length < 2) { toast("Välj minst två personer."); return; }
  const tag = addTag(addTagCtx.photoId, "co_presence", name, { visibility: segVal("visSeg") });
  selected.forEach((id) => addRef(tag.id, "entity", id));
  toast(`Skapade gruppen "${name}" med ${selected.length} personer.`);
  closeAddTagModal();
}

// --------------------------------------------------------- share as album

function albumPhotosFor(category, text) {
  const matching = DB.tags.filter((t) => t.category === category && t.tag.toLowerCase() === text.toLowerCase());
  const seen = new Set();
  const rows = [];
  matching.forEach((t) => {
    if (seen.has(t.photoId)) return;
    seen.add(t.photoId);
    const photo = DB.photos.find((p) => p.id === t.photoId);
    const forcedPrivate = photoHasPrivacyTag(photo.id);
    const excluded = t.visibility === "private" || forcedPrivate;
    rows.push({ photo, tag: t, excluded, reason: forcedPrivate ? "sekretesstagg på bilden" : (t.visibility === "private" ? "den här taggen är privat" : null) });
  });
  return rows;
}

function openShareTagAlbum(category, encodedText) {
  const text = decodeURIComponent(encodedText);
  renderShareTagAlbum(category, text);
  document.getElementById("shareTagModal").classList.remove("hidden");
}
function closeShareTagModal() { document.getElementById("shareTagModal").classList.add("hidden"); }
function renderShareTagAlbum(category, text) {
  const rows = albumPhotosFor(category, text);
  const shareable = rows.filter((r) => !r.excluded).length;
  document.getElementById("shareTagModalBody").innerHTML = `
    <button class="lb-btn lb-close" onclick="closeShareTagModal()">${icon("close")}</button>
    <h2>${icon("share")}Dela "${escapeHtml(text)}" som album</h2>
    <p class="section-sub small">Varje bild som inte visas gråtonad delas. Privata bilder visas gråtonade här och ingår inte i delningen — se UX_FLOWS.md:s förhandsgranskning.</p>
    <div class="share-preview-grid">
      ${rows.map((r) => `<div class="share-preview-item ${r.excluded ? "blurred" : ""}" style="background:${r.photo.color}" title="${escapeHtml(r.photo.label)}">
        ${r.photo.emoji}
        ${r.excluded ? `<div class="excluded-badge">${icon("lock")}Privat — ${r.reason}</div>` : ""}
      </div>`).join("")}
    </div>
    <div class="row" style="margin-bottom:0.8rem;">
      ${rows.filter((r) => r.reason !== "sekretesstagg på bilden").map((r) => `
        <button class="btn small ghost" onclick="toggleAlbumItemVisibility('${r.tag.id}', '${category}', '${encodeURIComponent(text)}')">
          ${icon(r.tag.visibility === "shareable" ? "public" : "lock")}${escapeHtml(r.photo.label)}: ${r.tag.visibility === "shareable" ? "delningsbar" : "privat"}
        </button>`).join("")}
    </div>
    <p class="hint">${shareable} av ${rows.length} bilder delas just nu.</p>
    <div class="row"><button class="btn primary" onclick="confirmShareAlbum('${category}', '${encodeURIComponent(text)}')">${icon("check")}Bekräfta delning</button></div>
  `;
}
function toggleAlbumItemVisibility(tagId, category, encodedText) {
  const tag = DB.tags.find((t) => t.id === tagId);
  tag.visibility = tag.visibility === "private" ? "shareable" : "private";
  renderShareTagAlbum(category, decodeURIComponent(encodedText));
}
function confirmShareAlbum(category, encodedText) {
  const text = decodeURIComponent(encodedText);
  const rows = albumPhotosFor(category, text);
  const shareable = rows.filter((r) => !r.excluded).length;
  toast(`(mock) Delade albumet "${text}" — ${shareable} bild${shareable === 1 ? "" : "er"} synliga för mottagaren, ${rows.length - shareable} hölls privata.`);
  closeShareTagModal();
  renderPhotoDetail(openPhotoId);
}

// -------------------------------------------------------------- search UI

function buildRelationshipGraph() {
  const edges = [];
  DB.tags.filter((t) => t.category === "relationship").forEach((rt) => {
    const refs = DB.tagReferences.filter((r) => r.tagId === rt.id);
    const subj = refs.find((r) => r.role === "subject");
    const obj = refs.find((r) => r.role === "object");
    if (!subj || !obj) return;
    const subjTag = DB.tags.find((t) => t.id === subj.referenceValue);
    const objTag = DB.tags.find((t) => t.id === obj.referenceValue);
    if (!subjTag || !objTag) return;
    const eA = tagEntity(subjTag.id);
    const eB = tagEntity(objTag.id);
    if (eA && eB) edges.push({ a: eA.id, b: eB.id, label: rt.tag });
  });
  return edges;
}
function photosForEntity(entityId) {
  const tagIds = DB.tagReferences.filter((r) => r.referenceKind === "entity" && r.referenceValue === entityId).map((r) => r.tagId);
  return [...new Set(DB.tags.filter((t) => tagIds.includes(t.id)).map((t) => t.photoId))];
}
function matchEntities(query) {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  return Object.values(DB.entities).filter((e) => e.displayName.toLowerCase().includes(q));
}
function matchPlainTags(query) {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  return DB.tags.filter((t) => !ENTITY_CATEGORIES.includes(t.category) && t.tag.toLowerCase().includes(q));
}

function runSearch(query) {
  const entities = matchEntities(query);
  const plainTags = matchPlainTags(query);
  const directPhotoIds = new Set();
  entities.forEach((e) => photosForEntity(e.id).forEach((pid) => directPhotoIds.add(pid)));
  plainTags.forEach((t) => directPhotoIds.add(t.photoId));

  const edges = buildRelationshipGraph();
  const adj = {};
  edges.forEach(({ a, b, label }) => {
    (adj[a] = adj[a] || []).push({ to: b, label, from: a, target: b });
    (adj[b] = adj[b] || []).push({ to: a, label, from: a, target: b });
  });
  const visited = new Set(entities.map((e) => e.id));
  let frontier = entities.map((e) => ({ id: e.id, path: [], hops: 0 }));
  const reached = new Map();
  while (frontier.length) {
    const next = [];
    for (const node of frontier) {
      if (node.hops >= searchMaxHops) continue;
      for (const edge of adj[node.id] || []) {
        if (visited.has(edge.to)) continue;
        visited.add(edge.to);
        const path = [...node.path, { label: edge.label, fromName: DB.entities[edge.from].displayName, toName: DB.entities[edge.target].displayName }];
        reached.set(edge.to, { hops: node.hops + 1, path });
        next.push({ id: edge.to, path, hops: node.hops + 1 });
      }
    }
    frontier = next;
  }
  const relatedPhotos = [];
  const seenPhoto = new Set();
  reached.forEach((info, entityId) => {
    photosForEntity(entityId).forEach((pid) => {
      if (directPhotoIds.has(pid) || seenPhoto.has(pid)) return;
      seenPhoto.add(pid);
      relatedPhotos.push({ photoId: pid, path: info.path });
    });
  });
  return { entities, plainTags, directPhotoIds: [...directPhotoIds], relatedPhotos };
}

function renderSearchTab() {
  document.getElementById("searchPresets").innerHTML = ["Pappa", "Bella", "Björkparken", "Motorcykeln", "Kalas"]
    .map((q) => `<button class="chip-choice" onclick="document.getElementById('searchInput').value='${q}'; doSearch();">${q}</button>`).join("");
  if (lastSearchQuery) doSearch();
}
function doSearch() {
  const query = document.getElementById("searchInput").value;
  lastSearchQuery = query;
  searchMaxHops = 2;
  renderSearchResultsFor(query);
}
function expandSearchHops() {
  searchMaxHops = 6;
  renderSearchResultsFor(lastSearchQuery);
}
function searchResultRow(photoId, pathHtml) {
  const photo = DB.photos.find((p) => p.id === photoId);
  return `<div class="search-result-row">
    <span class="sr-emoji">${photo.emoji}</span>
    <div><div>${escapeHtml(photo.label)}</div>${pathHtml ? `<div class="sr-path">${pathHtml}</div>` : ""}</div>
  </div>`;
}
function renderSearchResultsFor(query) {
  const el = document.getElementById("searchResults");
  if (!query || !query.trim()) { el.innerHTML = ""; return; }
  const result = runSearch(query);
  if (!result.directPhotoIds.length && !result.relatedPhotos.length) {
    el.innerHTML = `<p class="empty-note">Inga träffar för "${escapeHtml(query)}".</p>`;
    return;
  }
  const directHtml = result.directPhotoIds.length
    ? result.directPhotoIds.map((pid) => searchResultRow(pid, "")).join("")
    : `<p class="empty-note">Inga direkta träffar.</p>`;
  const relatedHtml = result.relatedPhotos.length
    ? result.relatedPhotos.map((r) => searchResultRow(r.photoId, r.path.map((seg) => `${escapeHtml(seg.fromName)} —(${escapeHtml(seg.label)})→ ${escapeHtml(seg.toName)}`).join(" &middot; "))).join("")
    : `<p class="empty-note">Inga relaterade träffar via kopplingar${searchMaxHops < 3 ? " inom 2 steg" : ""}.</p>`;
  el.innerHTML = `
    <div class="search-tier">
      <div class="search-tier-label">${icon("check_circle")}Direkta träffar</div>
      ${directHtml}
    </div>
    <div class="search-tier">
      <div class="search-tier-label">${icon("hub")}Relaterat (via kopplingar, ${searchMaxHops < 3 ? "max 2 steg" : "utökat"})</div>
      ${relatedHtml}
      ${searchMaxHops < 3 ? `<button class="btn small ghost" onclick="expandSearchHops()">${icon("expand_more")}Visa fler steg (experimentellt)</button>` : ""}
    </div>
  `;
}

// -------------------------------------------------------------------- init

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("#tabNav .nav-pill").forEach((b) => b.addEventListener("click", () => switchTab(b.dataset.tab)));
  document.getElementById("searchBtn").addEventListener("click", doSearch);
  document.getElementById("searchInput").addEventListener("keydown", (e) => { if (e.key === "Enter") doSearch(); });
  document.querySelectorAll(".overlay").forEach((elx) => elx.addEventListener("click", (e) => {
    if (e.target !== elx) return;
    if (elx.id === "photoDetail") closePhotoDetail();
    else elx.classList.add("hidden");
  }));
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (!document.getElementById("addTagModal").classList.contains("hidden")) closeAddTagModal();
    else if (!document.getElementById("shareTagModal").classList.contains("hidden")) closeShareTagModal();
    else if (openPhotoId) closePhotoDetail();
  });
  render();
});
