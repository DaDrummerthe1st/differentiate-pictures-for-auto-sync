import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from .conftest import _SELENIUM_URL, _valid_access_token


def test_gallery_proactively_calls_refresh_before_token_expires(app_server):
    # ?test_refresh_ms speeds up the proactive silent-refresh timer so
    # the test doesn't have to wait out the real ~4 minute interval.
    # Doesn't use the shared `driver` fixture - needs the query param on
    # the very first navigation and to inject a fetch() spy before
    # clicking through to the gallery, ordering the shared fixture
    # doesn't give control over.
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1024,700")
    driver = webdriver.Remote(command_executor=_SELENIUM_URL, options=options)
    try:
        url = app_server + "/?test_refresh_ms=200"
        driver.get(url)
        driver.add_cookie({"name": "photo_server_access", "value": _valid_access_token(), "path": "/"})
        driver.get(url)

        # Recording fetch() calls, not relying on a real /refresh backend
        # - this test harness has no auth service behind it (see
        # conftest.py's app_server fixture), so the call will 404; what
        # matters here is that the client-side timer actually fires it.
        driver.execute_script(
            """
            window.__mpv_fetch_calls = [];
            const _f = window.fetch;
            window.fetch = function(url, opts) {
              window.__mpv_fetch_calls.push(String(url));
              return _f.apply(this, arguments);
            };
            """
        )
        driver.find_element(By.ID, "skipFolderBtn").click()
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, ".nav-pill")) == 3
        )

        time.sleep(0.6)  # >= 1 tick at the 200ms test interval

        calls = driver.execute_script("return window.__mpv_fetch_calls;")
        assert any(c.endswith("/refresh") for c in calls), f"expected a /refresh call, got {calls}"
    finally:
        driver.quit()
