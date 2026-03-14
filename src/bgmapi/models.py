from __future__ import annotations

from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubjectType(IntEnum):
    BOOK = 1
    ANIME = 2
    MUSIC = 3
    GAME = 4
    REAL = 6


class SubjectCollectionType(IntEnum):
    WISH = 1
    DONE = 2
    DOING = 3
    ON_HOLD = 4
    DROPPED = 5


class EpisodeCollectionType(IntEnum):
    NA = 0
    WISH = 1
    DONE = 2
    DROPPED = 3


class EpType(IntEnum):
    MAIN = 0
    SP = 1
    OP = 2
    ED = 3
    PROMO = 4
    MAD = 5
    OTHER = 6


class UserGroup(IntEnum):
    ADMIN = 1
    BANGUMI_ADMIN = 2
    DOUJIN_ADMIN = 3
    MUTED_USER = 4
    BLOCKED_USER = 5
    PERSON_ADMIN = 8
    WIKI_ADMIN = 9
    USER = 10
    WIKI_USER = 11


class SearchSort(StrEnum):
    MATCH = "match"
    HEAT = "heat"
    RANK = "rank"
    SCORE = "score"


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    @classmethod
    def from_api(cls, data: Any):
        return cls.model_validate(data)


class Avatar(ApiModel):
    large: str
    medium: str
    small: str


class Images(ApiModel):
    large: str
    common: str
    medium: str
    small: str
    grid: str


class SubjectTag(ApiModel):
    name: str
    count: int


class InfoBoxValue(ApiModel):
    key: str | None = Field(default=None, alias="k")
    value: str = Field(alias="v")


class InfoBoxItem(ApiModel):
    key: str
    value: str | list[InfoBoxValue]


class RatingCount(ApiModel):
    score_1: int = Field(alias="1")
    score_2: int = Field(alias="2")
    score_3: int = Field(alias="3")
    score_4: int = Field(alias="4")
    score_5: int = Field(alias="5")
    score_6: int = Field(alias="6")
    score_7: int = Field(alias="7")
    score_8: int = Field(alias="8")
    score_9: int = Field(alias="9")
    score_10: int = Field(alias="10")


class Rating(ApiModel):
    rank: int
    total: int
    score: float
    count: RatingCount


class CollectionSummary(ApiModel):
    wish: int
    collect: int
    doing: int
    on_hold: int
    dropped: int


class User(ApiModel):
    id: int
    username: str
    nickname: str
    user_group: UserGroup
    avatar: Avatar
    sign: str


class CurrentUser(User):
    email: str
    reg_time: datetime
    time_offset: int | None = None


class SlimSubject(ApiModel):
    id: int
    type: SubjectType
    name: str
    name_cn: str
    short_summary: str
    date: str | None = None
    images: Images
    volumes: int
    eps: int
    collection_total: int
    score: float
    rank: int
    tags: list[SubjectTag] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def _default_tags(cls, value: Any) -> Any:
        return [] if value is None else value


class Subject(ApiModel):
    id: int
    type: SubjectType
    name: str
    name_cn: str
    summary: str
    series: bool
    nsfw: bool
    locked: bool
    date: str | None = None
    platform: str
    images: Images
    infobox: list[InfoBoxItem] = Field(default_factory=list)
    volumes: int
    eps: int
    total_episodes: int
    rating: Rating
    collection: CollectionSummary
    meta_tags: list[str] = Field(default_factory=list)
    tags: list[SubjectTag] = Field(default_factory=list)

    @field_validator("infobox", "meta_tags", "tags", mode="before")
    @classmethod
    def _default_lists(cls, value: Any) -> Any:
        return [] if value is None else value


class PagedSubjects(ApiModel):
    total: int = 0
    limit: int = 0
    offset: int = 0
    data: list[Subject] = Field(default_factory=list)

    @field_validator("data", mode="before")
    @classmethod
    def _default_data(cls, value: Any) -> Any:
        return [] if value is None else value


class UserSubjectCollection(ApiModel):
    subject_id: int
    subject_type: SubjectType
    rate: int
    type: SubjectCollectionType
    comment: str | None = None
    tags: list[str]
    ep_status: int
    vol_status: int
    updated_at: datetime
    private: bool
    subject: SlimSubject | None = None


class Episode(ApiModel):
    id: int
    type: EpType | int
    name: str
    name_cn: str
    sort: float
    ep: int | None = None
    airdate: str
    comment: int
    duration: str
    desc: str
    disc: int
    duration_seconds: int | None = None
    subject_id: int | None = None


class UserEpisodeCollection(ApiModel):
    episode: Episode
    type: EpisodeCollectionType | int
    updated_at: int


class PagedUserEpisodeCollections(ApiModel):
    total: int = 0
    limit: int = 0
    offset: int = 0
    data: list[UserEpisodeCollection] = Field(default_factory=list)

    @field_validator("data", mode="before")
    @classmethod
    def _default_data(cls, value: Any) -> Any:
        return [] if value is None else value


class PagedUserSubjectCollections(ApiModel):
    total: int = 0
    limit: int = 0
    offset: int = 0
    data: list[UserSubjectCollection] = Field(default_factory=list)

    @field_validator("data", mode="before")
    @classmethod
    def _default_data(cls, value: Any) -> Any:
        return [] if value is None else value


class SubjectSearchFilter(ApiModel):
    subject_types: list[SubjectType] | None = Field(default=None, alias="type")
    meta_tags: list[str] | None = None
    tags: list[str] | None = Field(default=None, alias="tag")
    air_date: list[str] | None = None
    rating: list[str] | None = None
    rating_count: list[str] | None = None
    rank: list[str] | None = None
    nsfw: bool | None = None

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True, mode="json")


class CollectionUpdate(ApiModel):
    type: SubjectCollectionType | None = None
    rate: int | None = None
    ep_status: int | None = None
    vol_status: int | None = None
    comment: str | None = None
    private: bool | None = None
    tags: list[str] | None = None

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True, mode="json")


class Episode(ApiModel):
    airdate: str | None = None
    name: str
    name_cn: str
    duration: str | None = None
    desc: str | None = None
    ep: int
    sort: int | float
    id: int
    subject_id: int
    comment: int
    type: int
    disc: int
    duration_seconds: int | None = None


class EpisodeCollectionType(IntEnum):
    NA = 0
    WISH = 1
    DONE = 2
    DROPPED = 3


class EpisodeCollection(ApiModel):
    episode: Episode
    type: EpisodeCollectionType
    updated_at: int


class PagedEpisodeCollections(ApiModel):
    total: int = 0
    limit: int = 0
    offset: int = 0
    data: list[EpisodeCollection] = Field(default_factory=list)

    @field_validator("data", mode="before")
    @classmethod
    def _default_data(cls, value: Any) -> Any:
        return [] if value is None else value


class EpisodeCollectionUpdate(ApiModel):
    type: EpisodeCollectionType

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True, mode="json")
