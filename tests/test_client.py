from __future__ import annotations

import io
import json
from urllib import error

import pytest

from bgmapi import (
    BangumiApiError,
    BangumiClient,
    CollectionUpdate,
    EpisodeCollectionType,
    EpisodeCollectionUpdate,
    SubjectCollectionType,
    SubjectType,
)


class _FakeResponse:
    def __init__(self, body: str) -> None:
        self._body = body.encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_get_me_sends_bearer_and_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout):
        captured["timeout"] = timeout
        captured["url"] = req.full_url
        captured["authorization"] = req.get_header("Authorization")
        captured["user_agent"] = req.get_header("User-agent")
        return _FakeResponse(
            json.dumps(
                {
                    "id": 1,
                    "username": "sai",
                    "nickname": "Sai",
                    "user_group": 10,
                    "avatar": {
                        "large": "https://example.com/l.jpg",
                        "medium": "https://example.com/m.jpg",
                        "small": "https://example.com/s.jpg",
                    },
                    "sign": "hello",
                    "email": "sai@example.com",
                    "reg_time": "2022-08-06T19:43:23+08:00",
                    "time_offset": 8,
                }
            )
        )

    monkeypatch.setattr("bgmapi.client.request.urlopen", fake_urlopen)

    client = BangumiClient(token="token-value", user_agent="tester/bgmapi")
    me = client.get_me()

    assert me.username == "sai"
    assert me.avatar.large == "https://example.com/l.jpg"
    assert captured["url"] == "https://api.bgm.tv/v0/me"
    assert captured["authorization"] == "Bearer token-value"
    assert captured["user_agent"] == "tester/bgmapi"
    assert captured["timeout"] == 15.0


def test_collection_update_serializes_enum_values() -> None:
    update = CollectionUpdate(
        type=SubjectCollectionType.WISH,
        rate=9,
        tags=["动画"],
        private=False,
    )

    assert update.to_payload() == {
        "type": 1,
        "rate": 9,
        "tags": ["动画"],
        "private": False,
    }


def test_get_user_collections_sends_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        return _FakeResponse(
            json.dumps(
                {
                    "total": 1,
                    "limit": 20,
                    "offset": 40,
                    "data": [
                        {
                            "subject_id": 42,
                            "subject_type": 2,
                            "rate": 8,
                            "type": 3,
                            "comment": "追番中",
                            "tags": ["机战"],
                            "ep_status": 5,
                            "vol_status": 0,
                            "updated_at": "2022-08-06T19:43:23+08:00",
                            "private": False,
                            "subject": {
                                "id": 42,
                                "type": 2,
                                "name": "Test Name",
                                "name_cn": "测试条目",
                                "short_summary": "summary",
                                "date": "2020-01-01",
                                "images": {
                                    "large": "https://example.com/l.jpg",
                                    "common": "https://example.com/c.jpg",
                                    "medium": "https://example.com/m.jpg",
                                    "small": "https://example.com/s.jpg",
                                    "grid": "https://example.com/g.jpg",
                                },
                                "volumes": 0,
                                "eps": 12,
                                "collection_total": 100,
                                "score": 7.5,
                                "rank": 500,
                                "tags": [{"name": "机战", "count": 10}],
                            },
                        }
                    ],
                }
            )
        )

    monkeypatch.setattr("bgmapi.client.request.urlopen", fake_urlopen)

    client = BangumiClient(user_agent="tester/bgmapi")
    result = client.get_user_collections(
        "sai",
        subject_type=SubjectType.ANIME,
        collection_type=SubjectCollectionType.DOING,
        limit=20,
        offset=40,
    )

    assert (
        captured["url"]
        == "https://api.bgm.tv/v0/users/sai/collections?limit=20&offset=40&subject_type=2&type=3"
    )
    assert result.total == 1
    assert result.data[0].type == SubjectCollectionType.DOING
    assert result.data[0].subject is not None
    assert result.data[0].subject.name_cn == "测试条目"


def test_get_user_subject_episode_collections(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        return _FakeResponse(
            json.dumps(
                {
                    "total": 2,
                    "limit": 100,
                    "offset": 0,
                    "data": [
                        {
                            "episode": {
                                "id": 1600428,
                                "type": 0,
                                "name": "屠夫格鲁修",
                                "name_cn": "屠夫格鲁修",
                                "sort": 9,
                                "ep": 9,
                                "airdate": "2026-03-06",
                                "comment": 0,
                                "duration": "24m",
                                "desc": "",
                                "disc": 0,
                                "subject_id": 526979
                            },
                            "type": 2,
                            "updated_at": 1741910000
                        },
                        {
                            "episode": {
                                "id": 1600429,
                                "type": 0,
                                "name": "贵族的义务",
                                "name_cn": "贵族的义务",
                                "sort": 10,
                                "ep": 10,
                                "airdate": "2026-03-13",
                                "comment": 0,
                                "duration": "24m",
                                "desc": "",
                                "disc": 0,
                                "subject_id": 526979
                            },
                            "type": 0,
                            "updated_at": 0
                        }
                    ]
                }
            )
        )

    monkeypatch.setattr("bgmapi.client.request.urlopen", fake_urlopen)

    client = BangumiClient(token="token-value", user_agent="tester/bgmapi")
    page = client.get_user_subject_episode_collections(526979)

    assert captured["url"] == "https://api.bgm.tv/v0/users/-/collections/526979/episodes?limit=100&offset=0"
    assert page.total == 2
    assert page.data[0].episode.id == 1600428
    assert int(page.data[0].type) == 2


def test_patch_user_subject_episode_collections(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["authorization"] = req.get_header("Authorization")
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _FakeResponse("")

    monkeypatch.setattr("bgmapi.client.request.urlopen", fake_urlopen)

    client = BangumiClient(token="token-value", user_agent="tester/bgmapi")
    client.patch_user_subject_episode_collections(
        526979,
        [1600420, 1600421, 1600429],
        collection_type=EpisodeCollectionType.DONE,
    )

    assert captured["url"] == "https://api.bgm.tv/v0/users/-/collections/526979/episodes"
    assert captured["method"] == "PATCH"
    assert captured["authorization"] == "Bearer token-value"
    assert captured["body"] == {
        "episode_id": [1600420, 1600421, 1600429],
        "type": 2,
    }


def test_http_error_is_raised_with_parsed_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(req, timeout):
        raise error.HTTPError(
            req.full_url,
            404,
            "Not Found",
            hdrs=None,
            fp=io.BytesIO(
                json.dumps(
                    {
                        "title": "Not Found",
                        "description": "subject not found",
                        "details": {"path": "/v0/subjects/999999"},
                    }
                ).encode("utf-8")
            ),
        )

    monkeypatch.setattr("bgmapi.client.request.urlopen", fake_urlopen)

    client = BangumiClient(user_agent="tester/bgmapi")
    with pytest.raises(BangumiApiError) as exc_info:
        client.get_subject(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.description == "subject not found"
    assert exc_info.value.details == {"path": "/v0/subjects/999999"}


def test_get_episode_collection(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["authorization"] = req.get_header("Authorization")
        return _FakeResponse(
            json.dumps(
                {
                    "episode": {
                        "id": 1575940,
                        "subject_id": 515759,
                        "name": "北部高原の物流",
                        "name_cn": "北部高原的物流",
                        "airdate": "2026-02-13",
                        "ep": 5,
                        "sort": 33,
                        "comment": 170,
                        "type": 0,
                        "disc": 0,
                        "duration": "00:24:00",
                        "duration_seconds": 1440,
                        "desc": "..."
                    },
                    "type": 2,
                    "updated_at": 1773061592
                }
            )
        )

    monkeypatch.setattr("bgmapi.client.request.urlopen", fake_urlopen)

    client = BangumiClient(token="token-value", user_agent="tester/bgmapi")
    result = client.get_episode_collection(1575940)

    assert captured["url"] == "https://api.bgm.tv/v0/users/-/collections/-/episodes/1575940"
    assert captured["authorization"] == "Bearer token-value"
    assert result.type == EpisodeCollectionType.DONE
    assert result.episode.sort == 33


def test_get_subject_episode_collections(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        return _FakeResponse(
            json.dumps(
                {
                    "total": 1,
                    "limit": 30,
                    "offset": 0,
                    "data": [
                        {
                            "episode": {
                                "id": 1575940,
                                "subject_id": 515759,
                                "name": "北部高原の物流",
                                "name_cn": "北部高原的物流",
                                "airdate": "2026-02-13",
                                "ep": 5,
                                "sort": 33,
                                "comment": 170,
                                "type": 0,
                                "disc": 0,
                                "duration": "00:24:00",
                                "duration_seconds": 1440,
                                "desc": "..."
                            },
                            "type": 2,
                            "updated_at": 1773061592
                        }
                    ]
                }
            )
        )

    monkeypatch.setattr("bgmapi.client.request.urlopen", fake_urlopen)

    client = BangumiClient(token="token-value", user_agent="tester/bgmapi")
    result = client.get_subject_episode_collections(515759)

    assert captured["url"] == "https://api.bgm.tv/v0/users/-/collections/515759/episodes?limit=30&offset=0"
    assert result.total == 1
    assert result.data[0].episode.id == 1575940
    assert result.data[0].type == EpisodeCollectionType.DONE


def test_put_episode_collection(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout):
        captured["method"] = req.get_method()
        captured["url"] = req.full_url
        captured["authorization"] = req.get_header("Authorization")
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _FakeResponse("")

    monkeypatch.setattr("bgmapi.client.request.urlopen", fake_urlopen)

    client = BangumiClient(token="token-value", user_agent="tester/bgmapi")
    client.put_episode_collection(
        1575940,
        EpisodeCollectionUpdate(type=EpisodeCollectionType.DONE),
    )

    assert captured["method"] == "PUT"
    assert captured["url"] == "https://api.bgm.tv/v0/users/-/collections/-/episodes/1575940"
    assert captured["authorization"] == "Bearer token-value"
    assert captured["body"] == {"type": 2}
