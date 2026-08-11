import unittest

from cache import TTLCache


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class TestTTLCache(unittest.TestCase):
    def test_set_and_get(self):
        cache = TTLCache(maxsize=2, ttl=10, clock=FakeClock())
        cache.set("a", 1)
        self.assertEqual(cache.get("a"), 1)

    def test_missing_key_returns_default(self):
        cache = TTLCache(maxsize=2, ttl=10, clock=FakeClock())
        self.assertIsNone(cache.get("nope"))
        self.assertEqual(cache.get("nope", "fallback"), "fallback")

    def test_evicts_least_recently_used_when_full(self):
        cache = TTLCache(maxsize=2, ttl=10, clock=FakeClock())
        cache.set("a", 1)
        cache.set("b", 2)
        cache.get("a")
        cache.set("c", 3)
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("a"), 1)

    def test_expired_entry_is_a_miss(self):
        clock = FakeClock()
        cache = TTLCache(maxsize=2, ttl=10, clock=clock)
        cache.set("a", 1)
        clock.advance(11)
        self.assertIsNone(cache.get("a"))
