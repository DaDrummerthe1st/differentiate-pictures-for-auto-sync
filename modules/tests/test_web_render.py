from modules.objects import Detection, DetectionResult
from modules.pictures import PictureLocation
from modules.quality import QualityResult
from modules.web.render import render_detail_page, render_grid_page, render_scan_page

_LOCATION = PictureLocation(
    picture_id="pic-1",
    location_id="loc-1",
    path="/photos/holiday/beach.jpg",
    md5="abc123",
    source=None,
    file_metadata={},
)


def test_render_scan_page_has_a_folder_form():
    html = render_scan_page()

    assert "<form" in html
    assert 'name="folder"' in html
    assert "/scan" in html


def test_render_scan_page_shows_an_error_message_when_given_one():
    html = render_scan_page(message="No such folder: /nope")

    assert "No such folder: /nope" in html


def test_render_grid_page_links_each_thumbnail_to_its_detail_page():
    html = render_grid_page(
        entries=[(_LOCATION, False)],
        folder="/photos/holiday",
        page=0,
        page_count=1,
        start_index=1,
        end_index=1,
        total_count=1,
    )

    assert 'href="/picture/loc-1"' in html
    assert 'src="/image/loc-1?variant=thumb"' in html
    assert "beach.jpg" in html


def test_render_grid_page_shows_a_badge_only_for_entries_with_detected_objects():
    with_objects = PictureLocation(
        picture_id="pic-2", location_id="loc-2", path="/photos/holiday/dog.jpg",
        md5="d1", source=None, file_metadata={},
    )
    html = render_grid_page(
        entries=[(_LOCATION, False), (with_objects, True)],
        folder="/photos/holiday",
        page=0,
        page_count=1,
        start_index=1,
        end_index=2,
        total_count=2,
    )

    # Two entries rendered, only one carries the has-objects badge span.
    assert html.count('class="thumb-entry"') == 2
    assert html.count('<span class="has-objects-badge">') == 1


def test_render_grid_page_shows_pagination_summary_and_nav_links():
    html = render_grid_page(
        entries=[(_LOCATION, False)],
        folder="/photos/holiday",
        page=1,
        page_count=3,
        start_index=21,
        end_index=21,
        total_count=41,
    )

    assert "21-21 of 41" in html
    assert "page 2/3" in html
    assert 'href="/pictures?folder=%2Fphotos%2Fholiday&amp;page=0"' in html  # Prev
    assert 'href="/pictures?folder=%2Fphotos%2Fholiday&amp;page=2"' in html  # Next


def test_render_grid_page_omits_prev_link_on_first_page():
    html = render_grid_page(
        entries=[(_LOCATION, False)], folder="/photos/holiday", page=0, page_count=2,
        start_index=1, end_index=1, total_count=21,
    )

    assert "Prev" not in html


def test_render_grid_page_omits_next_link_on_last_page():
    html = render_grid_page(
        entries=[(_LOCATION, False)], folder="/photos/holiday", page=1, page_count=2,
        start_index=21, end_index=21, total_count=21,
    )

    assert "Next" not in html


def test_render_detail_page_shows_findings_and_full_image():
    result = DetectionResult(
        detections=[Detection(class_name="dog", confidence=0.9, bbox=(1, 2, 3, 4))],
        image_width=800,
        image_height=600,
    )
    quality = QualityResult(blur=12.0, exposure=-5.0, saturation=60.0)

    html = render_detail_page(
        _LOCATION,
        exif=["Camera: Acme Camera 3000"],
        quality=quality,
        objects_result=result,
        folder="/photos/holiday",
        page=0,
    )

    assert "beach.jpg" in html
    assert "Camera: Acme Camera 3000" in html
    assert "dog" in html
    assert 'src="/image/loc-1?variant=full"' in html
    assert 'href="/pictures?folder=%2Fphotos%2Fholiday&amp;page=0"' in html


def test_render_detail_page_reports_no_objects_detected():
    result = DetectionResult(detections=[], image_width=800, image_height=600)
    quality = QualityResult(blur=1.0, exposure=1.0, saturation=1.0)

    html = render_detail_page(
        _LOCATION, exif=["(none)"], quality=quality, objects_result=result, folder="/photos/holiday", page=0
    )

    assert "none detected" in html.lower()
