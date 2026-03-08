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

## Notes

- Bangumi recommends a descriptive `User-Agent` containing developer identity and app name.
- The example script is in `examples/basic.py`.
- The client uses `Authorization: Bearer <token>` for authenticated endpoints.
