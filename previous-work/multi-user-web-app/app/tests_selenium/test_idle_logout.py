import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from .conftest import _SELENIUM_URL, _valid_access_token


def test_silent_refresh_stops_after_idle_timeout(app_server):
    # test_idle_ms is tiny and well below test_refresh_ms's first tick,
    # so by the time the timer ever checks, "no activity since page
    # load" already counts as idle - isolates the idle-skip behavior
    # without needing to race real timing.
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1024,700")
    driver = webdriver.Remote(command_executor=_SELENIUM_URL, options=options)
    try:
        url = app_server + "/?test_refresh_ms=200&test_idle_ms=50"
        driver.get(url)
        driver.add_cookie({"name": "photo_server_access", "value": _valid_access_token(), "path": "/"})
        driver.get(url)

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
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, ".nav-pill")) == 3
        )

        time.sleep(0.6)  # several 200ms ticks would fire if not for idle-skip

        calls = driver.execute_script("return window.__mpv_fetch_calls;")
        assert not any(c.endswith("/refresh") for c in calls), (
            f"expected no /refresh calls once idle, got {calls}"
        )
    finally:
        driver.quit()
