from __future__ import annotations

import io
import json
from urllib import error

import pytest

from bgmapi import BangumiApiError, BangumiClient, CollectionUpdate, SubjectCollectionType


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
