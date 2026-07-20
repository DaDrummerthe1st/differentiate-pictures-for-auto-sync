import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def _wait_for_pills(driver, count=3):
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, ".nav-pill")) == count
    )


def _dom_albums(driver):
    # Only the active album is ever built into the DOM - a hidden album
    # isn't just visually hidden, its nodes (and thumbnail <img> tags)
    # don't exist at all. So "which album is showing" and "how many
    # album nodes exist" are the same question here.
    return [a.get_attribute("data-headline") for a in driver.find_elements(By.CSS_SELECTOR, "#tree .album")]


def test_only_one_album_in_the_dom_on_load(driver):
    _wait_for_pills(driver)
    WebDriverWait(driver, 10).until(lambda d: len(_dom_albums(d)) == 1)
    assert _dom_albums(driver) == ["AlbumA"]


def test_hidden_albums_have_no_dom_nodes_at_all(driver):
    _wait_for_pills(driver)
    WebDriverWait(driver, 10).until(lambda d: len(_dom_albums(d)) == 1)
    # Not just "not visible" - genuinely absent, no thumbnail <img>
    # elements built for them at all.
    assert driver.find_elements(By.CSS_SELECTOR, '.album[data-headline="AlbumB"]') == []
    assert driver.find_elements(By.CSS_SELECTOR, '.album[data-headline="AlbumC"]') == []


def test_clicking_a_nav_pill_switches_the_album_in_the_dom(driver):
    _wait_for_pills(driver)
    driver.find_element(By.CSS_SELECTOR, '.nav-pill[data-headline="AlbumB"]').click()

    WebDriverWait(driver, 10).until(lambda d: _dom_albums(d) == ["AlbumB"])
    assert _dom_albums(driver) == ["AlbumB"]

    driver.find_element(By.CSS_SELECTOR, '.nav-pill[data-headline="AlbumC"]').click()
    WebDriverWait(driver, 10).until(lambda d: _dom_albums(d) == ["AlbumC"])
    assert _dom_albums(driver) == ["AlbumC"]


def test_current_nav_pill_is_marked(driver):
    _wait_for_pills(driver)
    driver.find_element(By.CSS_SELECTOR, '.nav-pill[data-headline="AlbumB"]').click()
    WebDriverWait(driver, 10).until(lambda d: _dom_albums(d) == ["AlbumB"])

    pills = {
        p.get_attribute("data-headline"): "current" in p.get_attribute("class").split()
        for p in driver.find_elements(By.CSS_SELECTOR, ".nav-pill")
    }
    assert pills == {"AlbumA": False, "AlbumB": True, "AlbumC": False}


def test_active_album_persists_across_reload(driver, app_server):
    _wait_for_pills(driver)
    driver.find_element(By.CSS_SELECTOR, '.nav-pill[data-headline="AlbumC"]').click()
    WebDriverWait(driver, 10).until(lambda d: _dom_albums(d) == ["AlbumC"])

    driver.get(app_server + "/")
    _wait_for_pills(driver)
    time.sleep(0.2)
    assert _dom_albums(driver) == ["AlbumC"]
