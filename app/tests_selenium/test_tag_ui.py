from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


def _open_lightbox(driver, thumb_index=0):
    # app_server is module-scoped (one shared sqlite tags table for every
    # test in this file), so tests that actually save a tag each use their
    # own thumbnail - otherwise a tag from an earlier test leaks into a
    # later test's chip-count/content assertions for the same photo.
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, ".thumb")) > thumb_index
    )
    driver.find_elements(By.CSS_SELECTOR, ".thumb")[thumb_index].click()
    WebDriverWait(driver, 10).until(
        lambda d: "hidden" not in d.find_element(By.ID, "lightbox").get_attribute("class")
    )


def _fill_and_save_tag(driver, category, value):
    WebDriverWait(driver, 10).until(
        lambda d: "hidden" not in d.find_element(By.ID, "tagForm").get_attribute("class")
    )
    Select(driver.find_element(By.ID, "tagCategorySelect")).select_by_value(category)
    value_input = driver.find_element(By.ID, "tagValueInput")
    value_input.clear()
    value_input.send_keys(value)
    driver.find_element(By.ID, "tagFormSave").click()
    WebDriverWait(driver, 10).until(
        lambda d: "hidden" in d.find_element(By.ID, "tagForm").get_attribute("class")
    )


def test_add_tag_button_opens_form(driver):
    _open_lightbox(driver)
    driver.find_element(By.ID, "lbAddTagBtn").click()
    WebDriverWait(driver, 10).until(
        lambda d: "hidden" not in d.find_element(By.ID, "tagForm").get_attribute("class")
    )
    assert "hidden" in driver.find_element(By.ID, "tagFormDelete").get_attribute("class")


def test_create_whole_photo_tag_shows_as_chip(driver):
    _open_lightbox(driver, thumb_index=1)
    driver.find_element(By.ID, "lbAddTagBtn").click()
    _fill_and_save_tag(driver, "places", "the beach")

    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "#lbTagChips .tag-chip")) == 1
    )
    chip = driver.find_element(By.CSS_SELECTOR, "#lbTagChips .tag-chip")
    assert "the beach" in chip.text


def test_edit_and_delete_a_tag_via_its_chip(driver):
    _open_lightbox(driver, thumb_index=2)
    driver.find_element(By.ID, "lbAddTagBtn").click()
    _fill_and_save_tag(driver, "places", "the beach")
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "#lbTagChips .tag-chip")) == 1
    )

    driver.find_element(By.CSS_SELECTOR, "#lbTagChips .tag-chip").click()
    WebDriverWait(driver, 10).until(
        lambda d: "hidden" not in d.find_element(By.ID, "tagForm").get_attribute("class")
    )
    # Editing (not creating) surfaces a delete button and pre-fills the value.
    assert "hidden" not in driver.find_element(By.ID, "tagFormDelete").get_attribute("class")
    assert driver.find_element(By.ID, "tagValueInput").get_attribute("value") == "the beach"

    driver.find_element(By.ID, "tagFormDelete").click()
    WebDriverWait(driver, 10).until(
        lambda d: "hidden" in d.find_element(By.ID, "tagForm").get_attribute("class")
    )
    WebDriverWait(driver, 10).until(
        lambda d: d.find_elements(By.CSS_SELECTOR, "#lbTagChips .tag-chip") == []
    )


def test_escape_closes_tag_form_but_not_lightbox(driver):
    _open_lightbox(driver)
    driver.find_element(By.ID, "lbAddTagBtn").click()
    WebDriverWait(driver, 10).until(
        lambda d: "hidden" not in d.find_element(By.ID, "tagForm").get_attribute("class")
    )
    driver.find_element(By.ID, "tagValueInput").send_keys(Keys.ESCAPE)
    WebDriverWait(driver, 10).until(
        lambda d: "hidden" in d.find_element(By.ID, "tagForm").get_attribute("class")
    )
    assert "hidden" not in driver.find_element(By.ID, "lightbox").get_attribute("class")


def test_drawing_a_box_on_the_image_opens_form_with_hint_and_creates_a_positioned_box(driver):
    _open_lightbox(driver, thumb_index=3)
    img = driver.find_element(By.ID, "lbImg")
    size = img.size
    assert size["width"] > 20 and size["height"] > 20

    # Anchored on move_to_element(img) (the element's center - unambiguous)
    # rather than move_to_element_with_offset's top-left-ish offset, whose
    # exact reference point (corner vs. center) varies by driver/protocol
    # version - a fixed pixel offset from the wrong reference point can
    # drag the cursor clean off this suite's small (40x30) test images and
    # outside #lbImageWrap, where the app's own stray-drag-cancel handler
    # (app.js) then cancels the whole gesture before a box is ever drawn.
    dx = min(10, size["width"] // 4)
    dy = min(10, size["height"] // 4)
    ActionChains(driver).move_to_element(img).move_by_offset(-dx, -dy).click_and_hold().move_by_offset(
        2 * dx, 2 * dy
    ).release().perform()

    WebDriverWait(driver, 10).until(
        lambda d: "hidden" not in d.find_element(By.ID, "tagForm").get_attribute("class")
    )
    assert "hidden" not in driver.find_element(By.ID, "tagFormHint").get_attribute("class")

    _fill_and_save_tag(driver, "people", "mother")

    WebDriverWait(driver, 10).until(lambda d: d.find_elements(By.CSS_SELECTOR, "#lbBoxes .tag-box"))
    box = driver.find_element(By.CSS_SELECTOR, "#lbBoxes .tag-box")
    assert box.value_of_css_property("width") not in ("0px", "auto")
    assert "mother" in box.find_element(By.CLASS_NAME, "tag-box-label").text
