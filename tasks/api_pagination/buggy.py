def paginate(items, limit, after=None):
    if limit <= 0:
        raise ValueError("limit must be positive")
    if after is None:
        start = 0
    else:
        start = next((i for i, item in enumerate(items) if item["id"] > after), len(items)) + 1  # BUG: skips first valid item
    page = items[start:start + limit]
    next_cursor = page[-1]["id"] if page and start + limit < len(items) else None
    return page, next_cursor
