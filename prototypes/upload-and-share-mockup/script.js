// Client-side only. Everything here fakes a response — no server involved,
// no data leaves this page. See documentation/upload-and-share/ for the
// real design; this is a clickable visual mockup of it, nothing more.

function wireSegmented(root) {
  root.querySelectorAll("[data-seg]").forEach((group) => {
    const buttons = group.querySelectorAll("button");
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.setAttribute("aria-pressed", "false"));
        btn.setAttribute("aria-pressed", "true");
      });
    });
  });
}

function wireToggles(root) {
  root.querySelectorAll(".toggle").forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const on = toggle.getAttribute("aria-pressed") === "true";
      toggle.setAttribute("aria-pressed", String(!on));
    });
  });
}

function wireShareDialog() {
  const modeButtons = document.querySelectorAll("#share-modes button");
  const usernameField = document.getElementById("field-username");
  const emailField = document.getElementById("field-email");
  const status = document.getElementById("share-status");
  const pendingList = document.getElementById("pending-list");
  let mode = "username";

  modeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      mode = btn.dataset.mode;
      modeButtons.forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
      usernameField.style.display = mode === "username" ? "flex" : "none";
      emailField.style.display = mode === "email" ? "flex" : "none";
      status.className = "status-msg";
    });
  });

  document.getElementById("share-send").addEventListener("click", () => {
    const terms = document.querySelector('#terms-toggle button[aria-pressed="true"]').dataset.terms;
    if (mode === "username") {
      const value = document.getElementById("username-input").value.trim();
      if (!value) { showStatus(status, "warn", "Enter a username first."); return; }
      // Simulated lookup: any name containing "x" is "not found", purely for the demo.
      if (value.toLowerCase().includes("x")) {
        showStatus(status, "warn", `No user found for "${value}".`);
      } else {
        showStatus(status, "ok", `Shared with ${value} (${terms}). A real photo_owners row would be created now.`);
      }
    } else {
      const value = document.getElementById("email-input").value.trim();
      if (!value || !value.includes("@")) { showStatus(status, "warn", "Enter a valid email first."); return; }
      showStatus(status, "ok", `Invite queued for ${value} (${terms}) — pending_shares row created.`);
      const li = document.createElement("li");
      li.innerHTML = `<span>${value}</span><span class="state">pending (${terms})</span>`;
      pendingList.prepend(li);
    }
  });
}

function showStatus(el, kind, text) {
  el.textContent = text;
  el.className = `status-msg show ${kind}`;
}

function wirePlatformShare() {
  const btn = document.getElementById("platform-share-btn");
  const status = document.getElementById("platform-share-status");
  btn.addEventListener("click", async () => {
    const shareData = {
      title: "A photo from DPFAS",
      text: "Shared via DPFAS (mock link, this page has no real backend)",
      url: window.location.href,
    };
    if (navigator.share) {
      try {
        await navigator.share(shareData);
        showStatus(status, "ok", "OS share sheet completed.");
      } catch (err) {
        showStatus(status, "warn", "Share sheet cancelled or failed: " + err.message);
      }
    } else {
      showStatus(status, "warn", "Web Share API not available in this browser — this is exactly the fallback case that opens the in-app dialog below instead.");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  wireSegmented(document);
  wireToggles(document);
  wireShareDialog();
  wirePlatformShare();
});
