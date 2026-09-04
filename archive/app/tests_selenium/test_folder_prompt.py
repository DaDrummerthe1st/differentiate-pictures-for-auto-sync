import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from .conftest import _SELENIUM_URL, _valid_access_token

# A fake FileSystemDirectoryHandle covering everything saveImage()'s
# real-folder branch touches (values() for primeUsedNames, getFileHandle
# + createWritable for the actual write) - real File System Access API
# dialogs can't be automated headlessly, so every test here drives the
# app against this stub instead of a real folder.
_FAKE_HANDLE_JS = """
function makeFakeDirHandle(name) {
  return {
    name: name,
    values: async function*() {},
    getFileHandle: async function(fname, opts) {
      return {
        name: fname,
        createWritable: async function() {
          return { write: async function(blob) {}, close: async function() {} };
        },
      };
    },
    removeEntry: async function(fname) {},
  };
}
"""


def _stub_picker_resolves(driver, folder_name="TestFolder"):
    driver.execute_script(
        _FAKE_HANDLE_JS
        + f"""
        window.__mpv_picker_calls = 0;
        window.showDirectoryPicker = function() {{
          window.__mpv_picker_calls++;
          return Promise.resolve(makeFakeDirHandle({folder_name!r}));
        }};
        """
    )


def _stub_picker_aborts(driver):
    driver.execute_script(
        """
        window.__mpv_picker_calls = 0;
        window.showDirectoryPicker = function() {
          window.__mpv_picker_calls++;
          const e = new Error("aborted");
          e.name = "AbortError";
          return Promise.reject(e);
        };
        """
    )


def _fresh_driver_at(app_server):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1024,700")
    driver = webdriver.Remote(command_executor=_SELENIUM_URL, options=options)
    url = app_server + "/"
    driver.get(url)
    driver.add_cookie({"name": "photo_server_access", "value": _valid_access_token(), "path": "/"})
    driver.get(url)
    return driver


def _open_lightbox_and_download(driver):
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, ".thumb")) > 0
    )
    driver.find_element(By.CSS_SELECTOR, ".thumb").click()
    driver.find_element(By.ID, "lbDownload").click()


def test_no_setup_screen_gallery_visible_before_any_interaction(app_server):
    driver = _fresh_driver_at(app_server)
    try:
        assert driver.find_elements(By.ID, "setup") == []
        gallery = driver.find_element(By.ID, "gallery")
        assert "hidden" not in gallery.get_attribute("class").split()
    finally:
        driver.quit()


def test_label_shows_browser_default_text_before_any_pick(driver):
    label = driver.find_element(By.ID, "downloadFolderLabel")
    assert "webbläsarens" in label.text


def test_clicking_label_lets_user_pick_folder_and_updates_label(driver):
    _stub_picker_resolves(driver, "MyPictures")
    driver.find_element(By.ID, "downloadFolderLabel").click()
    WebDriverWait(driver, 5).until(
        lambda d: "MyPictures" in d.find_element(By.ID, "downloadFolderLabel").text
    )
    label = driver.find_element(By.ID, "downloadFolderLabel")
    assert label.get_attribute("title") == "MyPictures"
    assert driver.execute_script("return window.__mpv_picker_calls;") == 1


def test_first_download_offers_folder_picker_once_then_not_again(driver):
    _stub_picker_aborts(driver)
    _open_lightbox_and_download(driver)
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return window.__mpv_picker_calls;") == 1
    )

    driver.find_element(By.ID, "lbDownload").click()
    time.sleep(0.3)
    assert driver.execute_script("return window.__mpv_picker_calls;") == 1


def test_declined_pick_is_remembered_across_reload(app_server):
    driver = _fresh_driver_at(app_server)
    try:
        _stub_picker_aborts(driver)
        _open_lightbox_and_download(driver)
        WebDriverWait(driver, 5).until(
            lambda d: d.execute_script("return window.__mpv_picker_calls;") == 1
        )

        driver.get(app_server + "/")
        _stub_picker_aborts(driver)
        _open_lightbox_and_download(driver)
        time.sleep(0.3)
        assert driver.execute_script("return window.__mpv_picker_calls;") == 0
    finally:
        driver.quit()
