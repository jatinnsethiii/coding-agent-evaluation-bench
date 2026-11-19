class TTLCache:
    def __init__(self, clock):
        self.clock = clock
        self.entries = {}

    def put(self, key, value, ttl_seconds):
        self.entries[key] = (value, self.clock() + ttl_seconds)

    def get(self, key):
        if key not in self.entries:
            return None
        value, expires = self.entries[key]
        if self.clock() > expires:  # BUG: equality should also expire
            del self.entries[key]
            return None
        return value
