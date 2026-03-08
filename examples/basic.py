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

    subject = client.get_subject(1)
    print(f"subject: {subject.name_cn or subject.name}, score={subject.rating.score}")

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

    try:
        collection = client.get_user_collection(me.username, subject.id)
        print(f"collection type: {collection.type.name}, rate={collection.rate}")
    except BangumiApiError as exc:
        if exc.status_code == 404:
            print("collection: not collected")
        else:
            raise

    update = CollectionUpdate(
        type=SubjectCollectionType.WISH,
        rate=8,
        tags=["示例", "科幻"],
        comment="SDK example payload",
        private=False,
    )
    print(update.to_payload())


if __name__ == "__main__":
    main()
