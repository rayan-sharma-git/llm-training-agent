"""Tests for the /files/* propose → view → apply/discard → rollback endpoints."""
from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes import router


@pytest.fixture
def client(tmp_path):
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return TestClient(app), tmp_path


def _make_project(tmp_path, filename="src/app.py", content="line1\nline2\n"):
    target = tmp_path / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return filename


def test_propose_list_get_flow(client):
    test_client, tmp_path = client
    name = _make_project(tmp_path)

    # Propose a change without modifying the file.
    resp = test_client.post(
        "/api/v1/files/propose",
        json={
            "filePath": name,
            "proposedContent": "line1\nline2_changed\nline3\n",
            "projectRoot": str(tmp_path),
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filePath"] == name
    assert data["status"] == "pending"
    assert "-line2" in data["diff"] and "+line2_changed" in data["diff"]
    assert (tmp_path / name).read_text(encoding="utf-8") == "line1\nline2\n"

    change_id = data["changeId"]

    # Listed without contents.
    resp = test_client.get("/api/v1/files/changes", params={"projectRoot": str(tmp_path)})
    assert resp.status_code == 200
    changes = resp.json()["changes"]
    assert len(changes) == 1
    assert "proposedContent" not in changes[0]

    # Fetched with contents.
    resp = test_client.get(
        f"/api/v1/files/changes/{change_id}", params={"projectRoot": str(tmp_path)}
    )
    assert resp.status_code == 200
    assert resp.json()["originalContent"] == "line1\nline2\n"


def test_apply_and_rollback(client):
    test_client, tmp_path = client
    name = _make_project(tmp_path)

    change_id = test_client.post(
        "/api/v1/files/propose",
        json={
            "filePath": name,
            "proposedContent": "new content\n",
            "projectRoot": str(tmp_path),
        },
    ).json()["changeId"]

    resp = test_client.post(
        f"/api/v1/files/changes/{change_id}/apply", json={"projectRoot": str(tmp_path)}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "applied"
    assert (tmp_path / name).read_text(encoding="utf-8") == "new content\n"

    # Discarding an applied change is rejected.
    resp = test_client.post(
        f"/api/v1/files/changes/{change_id}/discard", json={"projectRoot": str(tmp_path)}
    )
    assert resp.status_code == 409

    resp = test_client.post(
        f"/api/v1/files/changes/{change_id}/rollback", json={"projectRoot": str(tmp_path)}
    )
    assert resp.status_code == 200
    assert (tmp_path / name).read_text(encoding="utf-8") == "line1\nline2\n"


def test_discard_pending_change(client):
    test_client, tmp_path = client
    name = _make_project(tmp_path)

    change_id = test_client.post(
        "/api/v1/files/propose",
        json={
            "filePath": name,
            "proposedContent": "changed\n",
            "projectRoot": str(tmp_path),
        },
    ).json()["changeId"]

    resp = test_client.post(
        f"/api/v1/files/changes/{change_id}/discard", json={"projectRoot": str(tmp_path)}
    )
    assert resp.status_code == 200
    # File untouched.
    assert (tmp_path / name).read_text(encoding="utf-8") == "line1\nline2\n"
    # No longer listed as pending.
    changes = test_client.get(
        "/api/v1/files/changes", params={"projectRoot": str(tmp_path)}
    ).json()["changes"]
    assert all(c["changeId"] != change_id for c in changes)


def test_propose_rejects_missing_file_and_traversal(client):
    test_client, tmp_path = client
    _make_project(tmp_path)

    resp = test_client.post(
        "/api/v1/files/propose",
        json={"filePath": "missing.txt", "proposedContent": "x", "projectRoot": str(tmp_path)},
    )
    assert resp.status_code == 404

    resp = test_client.post(
        "/api/v1/files/propose",
        json={"filePath": "../outside.txt", "proposedContent": "x", "projectRoot": str(tmp_path)},
    )
    assert resp.status_code in (400, 422)

    resp = test_client.post(
        "/api/v1/files/propose",
        json={"filePath": "", "proposedContent": "x", "projectRoot": str(tmp_path)},
    )
    assert resp.status_code == 422


def test_pending_changes_survive_new_store_instance(client):
    test_client, tmp_path = client
    name = _make_project(tmp_path)
    data = test_client.post(
        "/api/v1/files/propose",
        json={
            "filePath": name,
            "proposedContent": "x\n",
            "projectRoot": str(tmp_path),
        },
    ).json()
    # Each request builds a fresh store; the proposal must persist on disk.
    resp = test_client.get(
        f"/api/v1/files/changes/{data['changeId']}", params={"projectRoot": str(tmp_path)}
    )
    assert resp.status_code == 200
