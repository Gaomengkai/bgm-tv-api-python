# bgmapi

Typed Bangumi API client for Python with Pydantic models.

## Install

```bash
uv sync
```

Or install it as a package:

```bash
uv pip install .
```

## Quick start

```python
from bgmapi import BangumiClient, SearchSort, SubjectSearchFilter, SubjectType

client = BangumiClient.from_token_file(
    "token.txt",
    user_agent="yourname/bgmapi-sdk-example (https://github.com/yourname/yourrepo)",
)

me = client.get_me()
subject = client.get_subject(1)
results = client.search_subjects(
    "攻壳机动队",
    sort=SearchSort.RANK,
    search_filter=SubjectSearchFilter(
        subject_types=[SubjectType.ANIME],
        nsfw=False,
    ),
)

print(me.username)
print(subject.name_cn or subject.name)
print(results.total)
```


## Episode collection example

For anime progress, Bangumi episode state is managed via episode collection endpoints rather than `collection.ep_status`.

```python
from bgmapi import BangumiClient, EpisodeCollectionType, EpisodeCollectionUpdate

client = BangumiClient.from_token_file(
    "token.txt",
    user_agent="yourname/bgmapi-sdk-example (https://github.com/yourname/yourrepo)",
)

# Mark subject 515759 episode sort 33 as watched after resolving the episode id.
client.put_episode_collection(
    1575940,
    EpisodeCollectionUpdate(type=EpisodeCollectionType.DONE),
)
```

## Notes

- Bangumi recommends a descriptive `User-Agent` containing developer identity and app name.
- The example script is in `examples/basic.py`.
- The client uses `Authorization: Bearer <token>` for authenticated endpoints.

## Episode progress

The client also supports anime episode collection/progress endpoints:

```python
from bgmapi import BangumiClient, EpisodeCollectionType

client = BangumiClient.from_token_file(
    "token.txt",
    user_agent="yourname/bgmapi-sdk-example (https://github.com/yourname/yourrepo)",
)

subject_id = 526979
page = client.get_user_subject_episode_collections(subject_id)

# Mark episodes as watched; Bangumi recalculates the subject progress.
client.patch_user_subject_episode_collections(
    subject_id,
    [1600420, 1600421, 1600429],
    collection_type=EpisodeCollectionType.DONE,
)
```
