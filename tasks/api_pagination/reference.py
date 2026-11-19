def paginate(items, limit, after=None):
    if limit <= 0:
        raise ValueError("limit must be positive")
    start = 0 if after is None else next((i for i, item in enumerate(items) if item["id"] > after), len(items))
    page = items[start:start + limit]
    next_cursor = page[-1]["id"] if page and start + limit < len(items) else None
    return page, next_cursor
