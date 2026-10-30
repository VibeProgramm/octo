"""A rejected recording must not return through a different route or an old cache."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
app_module = pytest.importorskip("app")
client = app_module.app.test_client()


@pytest.fixture
def excluded(monkeypatch):
    monkeypatch.setattr(app_module, "_BLOCKED_VIDEO_IDS", frozenset({"bad00000001"}))
    with app_module._SEARCH_CACHE_LOCK:
        app_module._SEARCH_CACHE.clear()
    with app_module._META_CACHE_LOCK:
        app_module._META_CACHE.clear()
    rows = [
        {"id": "bad00000001", "title": "Example Song", "channel": "Example", "duration": 180},
        {"id": "good0000001", "title": "Example Song", "channel": "Example", "duration": 181},
    ]
    monkeypatch.setattr(app_module, "_run", lambda *a, **kw: "\n".join(map(json.dumps, rows)))
    monkeypatch.setattr(app_module, "_with_facts", lambda payload: payload)
    yield


def test_ranked_search_excludes_recording_without_a_caller_skip(excluded):
    answer = client.get("/search?q=Example Song&duration=180&resolve=0")
    assert answer.status_code == 200
    assert answer.get_json()["video_id"] == "good0000001"


@pytest.mark.parametrize("hot", [False, True])
def test_meta_ignores_rejected_recording_in_old_caches(excluded, hot):
    key = "v3|example song"
    old = {"video_id": "bad00000001", "title": "Example Song", "duration": 180}
    app_module._meta_db_put(key, old)
    if hot:
        app_module._META_CACHE[key] = old
    answer = client.get("/meta?q=Example Song&duration=180")
    assert answer.status_code == 200
    assert answer.get_json()["video_id"] == "good0000001"


@pytest.mark.parametrize("route", ["stream", "facts", "download"])
def test_direct_access_is_denied_before_any_network_or_file_work(excluded, monkeypatch, route):
    def unexpected(*a, **kw):
        raise AssertionError("blocked recording must never reach the provider")
    monkeypatch.setattr(app_module, "_resolve_url", unexpected)
    monkeypatch.setattr(app_module, "_run", unexpected)
    answer = client.get(f"/{route}?id=bad00000001&dest=/music/test")
    assert answer.status_code == 410
    assert answer.get_json()["error"] == "recording_excluded"


def test_resolve_cannot_reuse_a_blocked_signed_url(excluded, monkeypatch):
    monkeypatch.setattr(app_module, "_url_cache_get", lambda _: "https://cached.invalid/audio")
    assert app_module._resolve_url("bad00000001") is None
