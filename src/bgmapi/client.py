from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib import error, parse, request

from .exceptions import BangumiApiError
from .models import (
    CollectionUpdate,
    CurrentUser,
    EpisodeCollection,
    EpisodeCollectionUpdate,
    PagedEpisodeCollections,
    PagedSubjects,
    PagedUserSubjectCollections,
    SearchSort,
    Subject,
    SubjectCollectionType,
    SubjectSearchFilter,
    SubjectType,
    UserSubjectCollection,
)


class BangumiClient:
    def __init__(
        self,
        token: str | None = None,
        *,
        user_agent: str,
        base_url: str = "https://api.bgm.tv",
        timeout: float = 15.0,
    ) -> None:
        if not user_agent.strip():
            raise ValueError("user_agent must not be empty")
        self.token = token.strip() if token else None
        self.user_agent = user_agent
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @classmethod
    def from_token_file(
        cls,
        token_path: str | Path,
        *,
        user_agent: str,
        base_url: str = "https://api.bgm.tv",
        timeout: float = 15.0,
    ) -> BangumiClient:
        token = Path(token_path).read_text(encoding="utf-8").strip()
        return cls(
            token,
            user_agent=user_agent,
            base_url=base_url,
            timeout=timeout,
        )

    def get_me(self) -> CurrentUser:
        payload = self._request_json("GET", "/v0/me", require_auth=True)
        return CurrentUser.from_api(payload)

    def get_subject(self, subject_id: int) -> Subject:
        payload = self._request_json("GET", f"/v0/subjects/{subject_id}")
        return Subject.from_api(payload)

    def search_subjects(
        self,
        keyword: str,
        *,
        limit: int = 10,
        offset: int = 0,
        sort: SearchSort = SearchSort.MATCH,
        search_filter: SubjectSearchFilter | None = None,
    ) -> PagedSubjects:
        body: dict[str, Any] = {"keyword": keyword, "sort": sort.value}
        if search_filter is not None:
            body["filter"] = search_filter.to_payload()
        payload = self._request_json(
            "POST",
            "/v0/search/subjects",
            params={"limit": limit, "offset": offset},
            json_body=body,
        )
        return PagedSubjects.from_api(payload)

    def get_user_collection(
        self,
        username: str,
        subject_id: int,
    ) -> UserSubjectCollection:
        payload = self._request_json(
            "GET",
            f"/v0/users/{parse.quote(username, safe='')}/collections/{subject_id}",
        )
        return UserSubjectCollection.from_api(payload)

    def get_user_collections(
        self,
        username: str,
        *,
        subject_type: SubjectType | None = None,
        collection_type: SubjectCollectionType | None = None,
        limit: int = 30,
        offset: int = 0,
    ) -> PagedUserSubjectCollections:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if subject_type is not None:
            params["subject_type"] = int(subject_type)
        if collection_type is not None:
            params["type"] = int(collection_type)
        payload = self._request_json(
            "GET",
            f"/v0/users/{parse.quote(username, safe='')}/collections",
            params=params,
        )
        return PagedUserSubjectCollections.from_api(payload)

    def upsert_collection(self, subject_id: int, update: CollectionUpdate) -> None:
        self._request_json(
            "POST",
            f"/v0/users/-/collections/{subject_id}",
            json_body=update.to_payload(),
            require_auth=True,
        )

    def patch_collection(self, subject_id: int, update: CollectionUpdate) -> None:
        self._request_json(
            "PATCH",
            f"/v0/users/-/collections/{subject_id}",
            json_body=update.to_payload(),
            require_auth=True,
        )

    def get_episode_collection(self, episode_id: int) -> EpisodeCollection:
        payload = self._request_json(
            "GET",
            f"/v0/users/-/collections/-/episodes/{episode_id}",
            require_auth=True,
        )
        return EpisodeCollection.from_api(payload)

    def get_subject_episode_collections(
        self,
        subject_id: int,
        *,
        limit: int = 30,
        offset: int = 0,
    ) -> PagedEpisodeCollections:
        payload = self._request_json(
            "GET",
            f"/v0/users/-/collections/{subject_id}/episodes",
            params={"limit": limit, "offset": offset},
            require_auth=True,
        )
        return PagedEpisodeCollections.from_api(payload)

    def put_episode_collection(
        self,
        episode_id: int,
        update: EpisodeCollectionUpdate,
    ) -> None:
        self._request_json(
            "PUT",
            f"/v0/users/-/collections/-/episodes/{episode_id}",
            json_body=update.to_payload(),
            require_auth=True,
        )

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        require_auth: bool = False,
    ) -> Any:
        if require_auth and not self.token:
            raise ValueError("this endpoint requires a bearer token")

        url = f"{self.base_url}{path}"
        if params:
            query = parse.urlencode(params)
            url = f"{url}?{query}"

        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        raw_body: bytes | None = None
        if json_body is not None:
            headers["Content-Type"] = "application/json"
            raw_body = json.dumps(json_body, ensure_ascii=False).encode("utf-8")

        req = request.Request(url=url, data=raw_body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                body = response.read().decode("utf-8").strip()
                if not body:
                    return None
                return json.loads(body)
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace").strip()
            details: Any | None = None
            title = exc.reason or "HTTPError"
            description = body or title
            if body:
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    payload = None
                if isinstance(payload, dict):
                    title = str(payload.get("title", title))
                    description = str(payload.get("description", description))
                    details = payload.get("details")
            raise BangumiApiError(exc.code, title, description, details) from None
