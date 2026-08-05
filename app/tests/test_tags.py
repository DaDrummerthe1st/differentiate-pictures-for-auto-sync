import os
import time

import jwt
import pytest

from app.main import db as _db

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


def _token(sub: str = "1") -> str:
    now = int(time.time())
    payload = {"sub": sub, "type": "access", "iat": now, "exp": now + 900, "jti": f"jti-{sub}"}
    return jwt.encode(payload, _SECRET, algorithm="HS256")


def _as_user(client, sub: str):
    client.cookies.set("photo_server_access", _token(sub))
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
    _as_user(client, "1")
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "user1 tag"})
    _as_user(client, "2")
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "user2 tag"})
    res = client.get("/api/tags", params={"p": PHOTO})
    values = [t["value"] for t in res.json()]
    assert values == ["user2 tag"]

    _as_user(client, "1")
    res = client.get("/api/tags", params={"p": PHOTO})
    values = [t["value"] for t in res.json()]
    assert values == ["user1 tag"]


def test_list_tags_rejects_unknown_photo_path(client):
    res = client.get("/api/tags", params={"p": "AlbumA/nope.jpg"})
    assert res.status_code == 404


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
    _as_user(client, "1")
    created = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"}
    ).json()
    _as_user(client, "2")
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
    _as_user(client, "1")
    created = client.post(
        "/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"}
    ).json()
    _as_user(client, "2")
    res = client.delete(f"/api/tags/{created['id']}")
    assert res.status_code == 404

    _as_user(client, "1")
    res = client.get("/api/tags", params={"p": PHOTO})
    assert [t["value"] for t in res.json()] == ["the beach"]


# --- value suggestions (poor-man's entity autocomplete) ---


def test_tag_value_suggestions_scoped_to_user_and_category(client):
    _as_user(client, "1")
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "people", "value": "mother"})
    client.post("/api/tags", json={"photo_path": OTHER_PHOTO, "category": "people", "value": "mother"})
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "places", "value": "the beach"})
    _as_user(client, "2")
    client.post("/api/tags", json={"photo_path": PHOTO, "category": "people", "value": "someone else"})

    _as_user(client, "1")
    res = client.get("/api/tags/values", params={"category": "people"})
    assert res.status_code == 200
    assert res.json() == ["mother"]


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
