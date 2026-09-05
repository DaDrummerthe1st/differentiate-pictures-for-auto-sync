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


def _drag_on_image(driver, dx_frac, dy_frac, start_offset=(-10, -10)):
    """Drag on #lbImg by a fraction of its rendered size, anchored on the
    element's center (unambiguous across driver/protocol versions - see
    the note this replaced in the original version of this test)."""
    img = driver.find_element(By.ID, "lbImg")
    size = img.size
    sx, sy = start_offset
    dx = int(size["width"] * dx_frac)
    dy = int(size["height"] * dy_frac)
    ActionChains(driver).move_to_element(img).move_by_offset(sx, sy).click_and_hold().move_by_offset(
        dx, dy
    ).release().perform()


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


def test_draw_box_tool_is_explicit_not_an_always_on_drag(driver):
    # Dragging on the photo with the tool not armed must do nothing - this
    # is the whole point of the redesign (2026-08-05): an always-on drag
    # would hijack scrolling/pinch gestures on a touch device, and was
    # also reported as feeling like "no way to actually draw" on desktop.
    _open_lightbox(driver, thumb_index=3)
    _drag_on_image(driver, 0.3, 0.3)
    assert "hidden" in driver.find_element(By.ID, "tagForm").get_attribute("class")
    assert "hidden" in driver.find_element(By.ID, "lbDrawingBox").get_attribute("class")


def test_too_small_a_drag_stays_armed_instead_of_silently_failing(driver):
    # Found live 2026-08-05: a too-small box used to just vanish with zero
    # feedback. Now: stay armed (button still says "cancel drawing") so
    # the user can immediately try again, rather than a same-as-doing-
    # nothing failure.
    _open_lightbox(driver, thumb_index=4)
    driver.find_element(By.ID, "lbDrawBoxBtn").click()
    assert driver.find_element(By.ID, "lbDrawBoxBtn").get_attribute("aria-pressed") == "true"

    _drag_on_image(driver, 0.001, 0.001, start_offset=(-2, -2))
    assert driver.find_element(By.ID, "lbDrawBoxBtn").text == "✕ Avbryt ritning"
    assert "hidden" in driver.find_element(By.ID, "tagForm").get_attribute("class")


def test_drawing_then_resizing_a_box_before_confirming(driver):
    _open_lightbox(driver, thumb_index=5)
    driver.find_element(By.ID, "lbDrawBoxBtn").click()

    _drag_on_image(driver, 0.3, 0.3)
    WebDriverWait(driver, 10).until(
        lambda d: "adjusting" in d.find_element(By.ID, "lbDrawingBox").get_attribute("class")
    )
    box_before = driver.find_element(By.ID, "lbDrawingBox")
    width_before = box_before.size["width"]
    assert driver.find_element(By.ID, "lbDrawBoxBtn").text == "✓ Klar med ruta"

    # Drag the bottom-right (se) resize handle further out to grow the box.
    handle = driver.find_element(By.CSS_SELECTOR, ".lb-box-handle-se")
    ActionChains(driver).move_to_element(handle).click_and_hold().move_by_offset(25, 25).release().perform()
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, "lbDrawingBox").size["width"] > width_before
    )

    driver.find_element(By.ID, "lbDrawBoxBtn").click()  # confirm -> opens tag form
    _fill_and_save_tag(driver, "people", "mother")

    WebDriverWait(driver, 10).until(lambda d: d.find_elements(By.CSS_SELECTOR, "#lbBoxes .tag-box"))
    box = driver.find_element(By.CSS_SELECTOR, "#lbBoxes .tag-box")
    assert box.value_of_css_property("width") not in ("0px", "auto")
    assert "mother" in box.find_element(By.CLASS_NAME, "tag-box-label").text


def test_escape_while_armed_cancels_drawing_without_closing_lightbox(driver):
    _open_lightbox(driver, thumb_index=6)
    driver.find_element(By.ID, "lbDrawBoxBtn").click()
    assert driver.find_element(By.ID, "lbDrawBoxBtn").get_attribute("aria-pressed") == "true"

    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, "lbDrawBoxBtn").get_attribute("aria-pressed") == "false"
    )
    assert "hidden" not in driver.find_element(By.ID, "lightbox").get_attribute("class")
