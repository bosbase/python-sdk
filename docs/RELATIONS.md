# Relations - Python SDK

Relations connect records across collections. The SDK lets you expand relations inline, filter across relations, and react to back-relations in realtime.

## Expanding Relations

```python
posts = pb.collection("posts").get_list(
    page=1,
    per_page=20,
    query={"expand": "author,comments.author"},
)

for record in posts["items"]:
    author = record["expand"]["author"]
    comments = record["expand"].get("comments") or []
```

- Use comma-separated paths for nested expands.
- Expand paths follow relation field names (`comments.author`).

## Filtering by Relations

```python
expr = pb.filter("author = {:author} && comments.id ?= {:comment}", {
    "author": pb.auth_store.record["id"],
    "comment": "comment123",
})

records = pb.collection("posts").get_list(query={"filter": expr})
```

`?=` checks whether the relation contains the provided value.

## Managing Relation Fields

### Setting Single Relations

```python
pb.collection("posts").update(
    "POST_ID",
    body={"author": "USER_ID"},
)
```

### Managing Many-to-Many Relations

Provide lists of record IDs:

```python
pb.collection("posts").update(
    "POST_ID",
    body={"tags": ["tag1", "tag2"]},
)
```

When using the `$append`/`$remove` modifiers:

```python
pb.collection("posts").update(
    "POST_ID",
    body={
        "tags+": ["tag3"],
        "tags-": ["tag1"],
    },
)
```

## Back-Relations

The backend automatically exposes back-relations so you can expand them without storing redundant fields. For example, if comments have a `post` relation, you can expand `comments_via_post` from the `posts` collection (depending on your schema naming).

Use the Admin UI “API preview” to confirm the generated back-relation name and then use it in `expand`.

## Realtime and Relations

Subscriptions use `<collection>/<topic>` syntax, so you can monitor relation changes:

```python
def on_comment(event):
    print(event["action"], event["record"]["content"])

pb.collection("comments").subscribe("*", on_comment, query={"expand": "post"})
```

When a relation is expanded in the subscription and the related record changes, the backend automatically emits an update event with the refreshed relation data.

## Tips

1. Use `fields` to limit relation payloads (`"fields": "id,title,author.name"`).
2. When building filters that involve large relation lists, prefer `@collection` lookups inside rules to keep the filter lean.
3. Reuse relation names consistently (e.g. `user`, not `userId`) for clean expand syntax.
4. Enable cascading deletes only when the domain model requires strong ownership; otherwise handle clean-up with triggers or cron jobs.
