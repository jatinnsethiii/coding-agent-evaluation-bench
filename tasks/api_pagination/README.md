# Exclusive-cursor API pagination

## Task
Implement `paginate(items, limit, after=None)`. `items` is a list of dictionaries containing unique, ascending integer `id` values. Return `(page, next_cursor)` where `page` holds up to `limit` records whose IDs are strictly greater than `after` (or starts from the beginning if `after is None`). `next_cursor` is the last returned ID if there are **more records remaining**, otherwise `None`. `limit` must be positive (`ValueError` if not). A cursor ID that does not exist should still work using numeric comparison. Do not mutate inputs.

This is a simplified in-memory implementation of an API pagination contract.
