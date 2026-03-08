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
    # Bangumi 官方要求非浏览器客户端提供可识别的 User-Agent。
    client = BangumiClient.from_token_file(
        "token.txt",
        user_agent="yourname/bgmapi-sdk-example (https://github.com/yourname/yourrepo)",
    )

    # 读取当前 token 对应的用户信息。
    me = client.get_me()
    print(f"current user: {me.nickname} (@{me.username})")
    print(f"registered at: {me.reg_time.isoformat()}")

    # 读取单个条目详情。
    subject = client.get_subject(1)
    display_name = subject.name_cn or subject.name
    print(f"subject: {display_name}, score={subject.rating.score}, rank={subject.rating.rank}")

    # 搜索动画条目示例。
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

    # 查询当前用户“正在看”的动画收藏，也就是通常说的“正在追的番”。
    watching = client.get_user_collections(
        me.username,
        subject_type=SubjectType.ANIME,
        collection_type=SubjectCollectionType.DOING,
        limit=30,
    )
    print(f"watching anime total: {watching.total}")
    for item in watching.data:
        if item.subject is None:
            print(f"- {item.subject_id}: <missing subject payload>")
            continue
        title = item.subject.name_cn or item.subject.name
        print(f"- {item.subject_id}: {title} (ep_status={item.ep_status}, rate={item.rate})")

    # 查询单个收藏记录；如果未收藏，Bangumi 会返回 404。
    try:
        collection = client.get_user_collection(me.username, subject.id)
        print(f"collection type: {collection.type.name}, rate={collection.rate}")
    except BangumiApiError as exc:
        if exc.status_code == 404:
            print("collection: not collected")
        else:
            raise

    # 演示更新收藏所需的 payload 结构。这里仅打印，不实际写入。
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
