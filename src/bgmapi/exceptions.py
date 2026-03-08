from __future__ import annotations

from typing import Any


class BangumiApiError(Exception):
    def __init__(
        self,
        status_code: int,
        title: str,
        description: str,
        details: Any | None = None,
    ) -> None:
        super().__init__(f"{status_code} {title}: {description}")
        self.status_code = status_code
        self.title = title
        self.description = description
        self.details = details
