from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

# Minimal login page per MOCKUP.md's Login screen spec: email, password,
# submit - nothing else. Three states only: success redirects to the
# thumbnail screen ("/", served by the photo-viewer behind the same
# reverse-proxy origin); failure and lockout show MOCKUP.md's exact
# wording, identical regardless of which of wrong-password/unknown-email/
# malformed-input caused it, so the response never discloses which.
_LOGIN_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Log in</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 20rem; margin: 4rem auto; padding: 0 1rem; }
  form { display: flex; flex-direction: column; gap: 0.75rem; }
  input { font-size: 1rem; padding: 0.5rem; }
  button { font-size: 1rem; padding: 0.5rem; cursor: pointer; }
  #message { min-height: 1.2rem; color: #b00020; word-break: break-word; }
</style>
</head>
<body>
<form id="loginForm">
  <input type="email" name="email" placeholder="Email" required autocomplete="username">
  <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
  <button type="submit">Log in</button>
  <div id="message" role="alert"></div>
</form>
<script>
const form = document.getElementById("loginForm");
const message = document.getElementById("message");
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  const email = form.email.value.trim();
  const password = form.password.value;
  if (!email || !password) {
    message.textContent = "Incorrect email or password";
    return;
  }
  const submitButton = form.querySelector("button");
  submitButton.disabled = true;
  try {
    const res = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (res.ok) {
      window.location.href = "/";
      return;
    }
    if (res.status === 429) {
      message.textContent = "Too many attempts, try again in a minute.";
    } else {
      message.textContent = "Incorrect email or password";
    }
  } catch (err) {
    message.textContent = "Incorrect email or password";
  } finally {
    submitButton.disabled = false;
  }
});
</script>
</body>
</html>
"""


@router.get("/login", response_class=HTMLResponse)
def login_page() -> HTMLResponse:
    return HTMLResponse(content=_LOGIN_HTML)
