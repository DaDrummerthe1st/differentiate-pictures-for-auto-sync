import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def _wait_for_albums(driver, count=3):
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "#tree .album")) == count
    )
    return driver.find_elements(By.CSS_SELECTOR, "#tree .album")


def _visible_albums(driver):
    return [
        a.get_attribute("data-headline")
        for a in driver.find_elements(By.CSS_SELECTOR, "#tree .album")
        if "hidden" not in a.get_attribute("class").split()
    ]


def test_only_one_album_visible_on_load(driver):
    _wait_for_albums(driver)
    visible = _visible_albums(driver)
    assert visible == ["AlbumA"], f"expected only AlbumA visible on load, got {visible}"


def test_clicking_a_nav_pill_switches_the_visible_album(driver):
    _wait_for_albums(driver)
    driver.find_element(By.CSS_SELECTOR, '.nav-pill[data-headline="AlbumB"]').click()

    WebDriverWait(driver, 10).until(lambda d: _visible_albums(d) == ["AlbumB"])
    assert _visible_albums(driver) == ["AlbumB"]

    driver.find_element(By.CSS_SELECTOR, '.nav-pill[data-headline="AlbumC"]').click()
    WebDriverWait(driver, 10).until(lambda d: _visible_albums(d) == ["AlbumC"])
    assert _visible_albums(driver) == ["AlbumC"]


def test_current_nav_pill_is_marked(driver):
    _wait_for_albums(driver)
    driver.find_element(By.CSS_SELECTOR, '.nav-pill[data-headline="AlbumB"]').click()
    WebDriverWait(driver, 10).until(lambda d: _visible_albums(d) == ["AlbumB"])

    pills = {
        p.get_attribute("data-headline"): "current" in p.get_attribute("class").split()
        for p in driver.find_elements(By.CSS_SELECTOR, ".nav-pill")
    }
    assert pills == {"AlbumA": False, "AlbumB": True, "AlbumC": False}


def test_active_album_persists_across_reload(driver, app_server):
    _wait_for_albums(driver)
    driver.find_element(By.CSS_SELECTOR, '.nav-pill[data-headline="AlbumC"]').click()
    WebDriverWait(driver, 10).until(lambda d: _visible_albums(d) == ["AlbumC"])

    driver.get(app_server + "/")
    driver.find_element(By.ID, "skipFolderBtn").click()
    _wait_for_albums(driver)
    time.sleep(0.2)
    assert _visible_albums(driver) == ["AlbumC"]
