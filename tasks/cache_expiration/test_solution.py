from solution import TTLCache


class Clock:
    now = 100.0
    def __call__(self):
        return self.now


def test_get_missing_key():
    cache = TTLCache(Clock())
    assert cache.get("missing") is None


def test_value_before_expiry():
    clock = Clock()
    cache = TTLCache(clock)
    cache.put("a", "value", 10)
    clock.now = 109.999
    assert cache.get("a") == "value"


def test_expires_at_exact_ttl_boundary():
    clock = Clock()
    cache = TTLCache(clock)
    cache.put("a", "value", 10)
    clock.now = 110.0
    assert cache.get("a") is None


def test_non_positive_ttl_is_immediately_expired():
    clock = Clock()
    cache = TTLCache(clock)
    cache.put("zero", 1, 0)
    cache.put("negative", 1, -2)
    assert cache.get("zero") is None
    assert cache.get("negative") is None


def test_overwrite_resets_expiry():
    clock = Clock()
    cache = TTLCache(clock)
    cache.put("a", 1, 1)
    clock.now = 100.5
    cache.put("a", 2, 10)
    clock.now = 101.0
    assert cache.get("a") == 2
