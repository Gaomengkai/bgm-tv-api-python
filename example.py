from pathlib import Path
import sys

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from bgmapi import (
    BangumiApiError,
    BangumiClient,
    CollectionUpdate,
    SearchSort,
    SubjectCollectionType,
    SubjectSearchFilter,
    SubjectType,
)


def main() -> None:
    client = BangumiClient.from_token_file(
        "token.txt",
        user_agent="yourname/bgmapi-sdk-example (https://github.com/yourname/yourrepo)",
    )

    me = client.get_me()
    print(f"current user: {me.nickname} (@{me.username})")
    print(f"registered at: {me.reg_time.isoformat()}")

    subject = client.get_subject(1)
    display_name = subject.name_cn or subject.name
    print(f"subject: {display_name}, score={subject.rating.score}, rank={subject.rating.rank}")

    results = client.search_subjects(
        "攻壳机动队",
        limit=3,
        sort=SearchSort.RANK,
        search_filter=SubjectSearchFilter(
            subject_types=[SubjectType.ANIME],
            nsfw=False,
        ),
    )
    print(f"search total: {results.total}")
    for item in results.data:
        title = item.name_cn or item.name
        print(f"- {item.id}: {title} ({item.rating.score})")

    try:
        collection = client.get_user_collection(me.username, subject.id)
        print(f"collection type: {collection.type.name}, rate={collection.rate}")
    except BangumiApiError as exc:
        if exc.status_code == 404:
            print("collection: not collected")
        else:
            raise

    example_update = CollectionUpdate(
        type=SubjectCollectionType.WISH,
        rate=8,
        tags=["示例", "科幻"],
        comment="SDK example payload",
        private=False,
    )
    print("write payload preview:", example_update.to_payload())
    print("call client.upsert_collection(subject.id, example_update) to write it.")


if __name__ == "__main__":
    main()
