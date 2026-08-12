import os
import time

import jwt
import pytest
from PIL import Image

from app import main as app_main
from app.main import db as _db
from app.tests.conftest import DEFAULT_TEST_USERNAME

_SECRET = os.environ["JWT_SECRET_KEY"]

PHOTO = "AlbumA/1/pic1.jpg"
OTHER_PHOTO = "AlbumA/1/pic2.jpg"


@pytest.fixture(autouse=True)
def _clear_tags_table():
    # The app's sqlite connection is a module-level singleton shared across
    # the whole test session (see conftest.py), unlike a fresh DB per test -
    # without this, tags created by one test leak into the next test's
    # exact-list assertions.
    _db.execute("DELETE FROM tags")
    _db.commit()
    yield


def _token(sub: str, username: str) -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "username": username,
        "type": "access",
        "iat": now,
        "exp": now + 900,
        "jti": f"jti-{sub}-{username}",
    }
    return jwt.encode(payload, _SECRET, algorithm="HS256")


def _ensure_photos_for(username: str) -> None:
    # DEFAULT_TEST_USERNAME's own PHOTO/OTHER_PHOTO already exist via
    # conftest's fixture tree - any other simulated account needs its own
    # copy under its own dpfas_media/<username>/ root before it can
    # successfully tag PHOTO/OTHER_PHOTO (create_tag/list_tags now
    # validate the path exists in the *caller's own* space, not a shared
    # library).
    root = app_main.get_user_photos_root(username) / "AlbumA" / "1"
    root.mkdir(parents=True, exist_ok=True)
    for name, color in (("pic1.jpg", "red"), ("pic2.jpg", "green")):
        path = root / name
        if not path.exists():
            Image.new("RGB", (40, 30), color=color).save(path, "JPEG")


def _as_user(client, sub: str, username: str = DEFAULT_TEST_USERNAME):
    _ensure_photos_for(username)
    client.cookies.set("photo_server_access", _token(sub, username))
    return client


# --- creating whole-photo tags (no bounding box) ---


def test_create_whole_photo_tag_returns_201_with_tag_fields(client):
    res = client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"})
    assert res.status_code == 201
    body = res.json()
    assert body["category"] == "places"
    assert body["value"] == "the beach"
    assert body["bbox"] is None
    assert body["source"] == "manual"
    assert "id" in body and "created_at" in body


def test_create_tag_strips_whitespace_from_value(client):
    res = client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "  the beach  "})
    assert res.status_code == 201
    assert res.json()["value"] == "the beach"


def test_create_tag_rejects_whitespace_only_value(client):
    res = client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "   "})
    assert res.status_code == 400


def test_create_tag_accepts_occasion_category(client):
    res = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "occasion", "value": "Midsommar"}
    )
    assert res.status_code == 201
    assert res.json()["category"] == "occasion"


def test_create_tag_rejects_unknown_category(client):
    res = client.post("/api/tags", json={"photo_path": PHOTO, "category": "spaceships", "value": "x"})
    assert res.status_code == 400


def test_create_tag_rejects_unknown_photo_path(client):
    res = client.post("/api/tags", json={"photo_path": "AlbumA/nope.jpg", "category": "places", "value": "x"})
    assert res.status_code == 404


def test_create_tag_rejects_path_traversal(client):
    res = client.post("/api/tags", json={"photo_path": "../../../etc/passwd", "category": "places", "value": "x"})
    assert res.status_code == 400


# --- creating bounding-box tags ---


def test_create_bounding_box_tag_returns_bbox(client):
    res = client.post(
        "/api/tags",
        json={
            "photo_path": PHOTO,
            "category": "people",
            "value": "mother",
            "bbox_x": 0.1,
            "bbox_y": 0.2,
            "bbox_w": 0.3,
            "bbox_h": 0.4,
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert body["bbox"] == {"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.4}


def test_create_tag_rejects_partial_bounding_box(client):
    res = client.post(
        "/api/tags",
        json={"photo_path": PHOTO, "category": "people", "value": "mother", "bbox_x": 0.1, "bbox_y": 0.2},
    )
    assert res.status_code == 400


@pytest.mark.parametrize(
    "bbox",
    [
        {"bbox_x": -0.1, "bbox_y": 0.0, "bbox_w": 0.2, "bbox_h": 0.2},
        {"bbox_x": 0.0, "bbox_y": 0.0, "bbox_w": 1.5, "bbox_h": 0.2},
        {"bbox_x": 0.9, "bbox_y": 0.0, "bbox_w": 0.5, "bbox_h": 0.2},
        {"bbox_x": 0.0, "bbox_y": 0.0, "bbox_w": 0.0, "bbox_h": 0.2},
        {"bbox_x": 0.0, "bbox_y": 0.0, "bbox_w": 0.2, "bbox_h": -0.2},
    ],
)
def test_create_tag_rejects_out_of_range_bounding_box(client, bbox):
    payload = {"photo_path": PHOTO, "category": "people", "value": "mother", **bbox}
    res = client.post("/api/tags", json=payload)
    assert res.status_code == 400


# --- listing ---


def test_list_tags_for_photo(client):
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"})
    client.post("/api/tags", json={"photo_path": OTHER_PHOTO, "category": "places", "value": "the mountains"})
    res = client.get("/api/tags", params={"p": PHOTO})
    assert res.status_code == 200
    values = [t["value"] for t in res.json()]
    assert values == ["the beach"]


def test_list_tags_scoped_to_owning_user_only(client):
    _as_user(client, "1", "testuser1")
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "user1 tag"})
    _as_user(client, "2", "testuser2")
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "user2 tag"})
    res = client.get("/api/tags", params={"p": PHOTO})
    values = [t["value"] for t in res.json()]
    assert values == ["user2 tag"]

    _as_user(client, "1", "testuser1")
    res = client.get("/api/tags", params={"p": PHOTO})
    values = [t["value"] for t in res.json()]
    assert values == ["user1 tag"]


def test_list_tags_rejects_unknown_photo_path(client):
    res = client.get("/api/tags", params={"p": "AlbumA/nope.jpg"})
    assert res.status_code == 404


# --- cross-user tag visibility: every account, admin included, only ever
# sees its own manual tags - auto tags (future detector pipeline, not
# built yet) are shared regardless of owner. There is no more admin
# bypass: per documentation/plans/deep-singing-firefly.md, "no cross-user
# access, no admin bypass" applies here too, not just to photo bytes. ---


def _insert_auto_tag(photo_path: str, category: str, value: str, owner_user_id: int = 999) -> None:
    # No endpoint writes source='auto' yet (that's the detector pipeline,
    # a later phase) - insert directly, same as a batch job would.
    now = "2026-01-01T00:00:00+00:00"
    _db.execute(
        "INSERT INTO tags (user_id, photo_path, category, value, source, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, 'auto', ?, ?)",
        (owner_user_id, photo_path, category, value, now, now),
    )
    _db.commit()


def test_list_tags_hides_another_users_manual_tag(client):
    # Also covers the retired admin-bypass: role carries no special tag
    # visibility anymore, so this holds for every account, admin included.
    _as_user(client, "1", "testuser1")
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "user1 tag"})

    _as_user(client, "2", "testuser2")
    res = client.get("/api/tags", params={"p": PHOTO})

    assert res.json() == []


def test_list_tags_shows_auto_tags_to_any_user_regardless_of_who_they_belong_to(client):
    _insert_auto_tag(PHOTO, "people", "Person")

    _as_user(client, "2", "testuser2")
    res = client.get("/api/tags", params={"p": PHOTO})

    assert [t["value"] for t in res.json()] == ["Person"]
    assert res.json()[0]["source"] == "auto"


def test_admin_read_visibility_does_not_grant_write_rights_over_anothers_manual_tag(client):
    _as_user(client, "1", "testuser1")
    created = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"}
    ).json()

    _as_user(client, "2", "testuser2")
    patch_res = client.patch(f"/api/tags/{created['id']}", json={"category": "places", "value": "hijacked"})
    delete_res = client.delete(f"/api/tags/{created['id']}")

    assert patch_res.status_code == 404
    assert delete_res.status_code == 404


# --- editing ---


def test_update_tag_changes_fields_and_updated_at(client):
    created = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"}
    ).json()
    res = client.patch(
        f"/api/tags/{created['id']}", json={"category": "places", "value": "the seaside"}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["value"] == "the seaside"
    assert body["updated_at"] >= created["updated_at"]


def test_update_tag_can_add_a_bounding_box_to_an_existing_whole_photo_tag(client):
    created = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "people", "value": "mother"}
    ).json()
    res = client.patch(
        f"/api/tags/{created['id']}",
        json={
            "category": "people",
            "value": "mother",
            "bbox_x": 0.0,
            "bbox_y": 0.0,
            "bbox_w": 0.5,
            "bbox_h": 0.5,
        },
    )
    assert res.status_code == 200
    assert res.json()["bbox"] == {"x": 0.0, "y": 0.0, "w": 0.5, "h": 0.5}


def test_update_tag_rejects_invalid_category(client):
    created = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"}
    ).json()
    res = client.patch(f"/api/tags/{created['id']}", json={"category": "nope", "value": "x"})
    assert res.status_code == 400


def test_update_nonexistent_tag_returns_404(client):
    res = client.patch("/api/tags/999999", json={"category": "places", "value": "x"})
    assert res.status_code == 404


def test_update_another_users_tag_returns_404(client):
    _as_user(client, "1", "testuser1")
    created = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"}
    ).json()
    _as_user(client, "2", "testuser2")
    res = client.patch(f"/api/tags/{created['id']}", json={"category": "places", "value": "hijacked"})
    assert res.status_code == 404


# --- deleting ---


def test_delete_tag_removes_it(client):
    created = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"}
    ).json()
    res = client.delete(f"/api/tags/{created['id']}")
    assert res.status_code == 204
    res = client.get("/api/tags", params={"p": PHOTO})
    assert res.json() == []


def test_delete_nonexistent_tag_returns_404(client):
    res = client.delete("/api/tags/999999")
    assert res.status_code == 404


def test_delete_another_users_tag_returns_404_and_leaves_it_intact(client):
    _as_user(client, "1", "testuser1")
    created = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"}
    ).json()
    _as_user(client, "2", "testuser2")
    res = client.delete(f"/api/tags/{created['id']}")
    assert res.status_code == 404

    _as_user(client, "1", "testuser1")
    res = client.get("/api/tags", params={"p": PHOTO})
    assert [t["value"] for t in res.json()] == ["the beach"]


# --- value suggestions (poor-man's entity autocomplete) ---


def test_tag_value_suggestions_scoped_to_user_and_category(client):
    _as_user(client, "1", "testuser1")
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "people", "value": "mother"})
    client.post("/api/tags", json={"photo_path": OTHER_PHOTO, "category": "people", "value": "mother"})
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"})
    _as_user(client, "2", "testuser2")
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "people", "value": "someone else"})

    _as_user(client, "1", "testuser1")
    res = client.get("/api/tags/values", params={"category": "people"})
    assert res.status_code == 200
    assert res.json() == ["mother"]


def test_tag_value_suggestions_no_longer_grants_admin_a_cross_user_view(client):
    _as_user(client, "1", "testuser1")
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "people", "value": "mother"})

    _as_user(client, "2", "testuser2")
    res = client.get("/api/tags/values", params={"category": "people"})

    assert res.json() == []


def test_tag_value_suggestions_rejects_unknown_category(client):
    res = client.get("/api/tags/values", params={"category": "nope"})
    assert res.status_code == 400


# --- auth gating ---


def test_create_tag_without_session_returns_401(client):
    client.cookies.delete("photo_server_access")
    res = client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "x"})
    assert res.status_code == 401


def test_list_tags_without_session_returns_401(client):
    client.cookies.delete("photo_server_access")
    res = client.get("/api/tags", params={"p": PHOTO})
    assert res.status_code == 401


def test_update_tag_without_session_returns_401(client):
    created = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"}
    ).json()
    client.cookies.delete("photo_server_access")
    res = client.patch(f"/api/tags/{created['id']}", json={"category": "places", "value": "x"})
    assert res.status_code == 401


def test_delete_tag_without_session_returns_401(client):
    created = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"}
    ).json()
    client.cookies.delete("photo_server_access")
    res = client.delete(f"/api/tags/{created['id']}")
    assert res.status_code == 401
