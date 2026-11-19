# Cache expiration at TTL boundary

## Task
Implement `TTLCache(clock).put(key, value, ttl_seconds)` and `get(key)`. `clock()` returns monotonic seconds. An entry is available only for times **strictly before** its expiry time: at exactly `put_time + ttl_seconds` it must be absent. A nonexistent or expired key must return `None`. A nonpositive TTL expires immediately. Overwriting a key resets its expiry.

The tests inject a deterministic fake clock to avoid timing flakiness.
