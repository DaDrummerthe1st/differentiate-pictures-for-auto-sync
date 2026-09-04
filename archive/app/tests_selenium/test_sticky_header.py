from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def test_album_nav_bar_not_covered_by_toolbar_after_scroll(driver):
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "#tree .album")) == 1
    )

    # Enough images exist in the active album (see conftest.py) that the
    # page is taller than the window - scroll partway down so both
    # sticky elements settle into their scrolled positions.
    driver.execute_script("window.scrollTo(0, 400);")

    toolbar_rect = driver.execute_script(
        "return document.getElementById('toolbar').getBoundingClientRect();"
    )
    nav_bar_rect = driver.execute_script(
        "return document.getElementById('albumNavBar').getBoundingClientRect();"
    )

    assert nav_bar_rect["top"] >= toolbar_rect["bottom"], (
        f"albumNavBar (top={nav_bar_rect['top']}) overlaps toolbar "
        f"(bottom={toolbar_rect['bottom']}) after scrolling"
    )
