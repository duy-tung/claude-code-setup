"""Hidden expiry/eviction contract for TTLCache."""
import unittest

from cache import TTLCache


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class TestExpiryContract(unittest.TestCase):
    def test_len_reports_only_live_entries(self):
        clock = FakeClock()
        cache = TTLCache(maxsize=4, ttl=10, clock=clock)
        cache.set("a", 1)
        cache.set("b", 2)
        clock.advance(11)
        cache.set("c", 3)
        self.assertEqual(len(cache), 1)

    def test_reading_an_expired_key_drops_it(self):
        clock = FakeClock()
        cache = TTLCache(maxsize=4, ttl=10, clock=clock)
        cache.set("a", 1)
        clock.advance(11)
        self.assertIsNone(cache.get("a"))
        self.assertEqual(len(cache), 0)

    def test_capacity_reclaims_expired_before_evicting_a_live_entry(self):
        clock = FakeClock()
        cache = TTLCache(maxsize=2, ttl=10, clock=clock)
        cache.set("stale", 1)
        clock.advance(6)
        cache.set("fresh", 2)   # written 6s later, still live at +11s
        clock.advance(5)        # stale is now 11s old, fresh is 5s old
        cache.set("new", 3)

        # "stale" is dead weight; sacrificing "fresh" instead loses live data.
        self.assertEqual(cache.get("fresh"), 2)
        self.assertEqual(cache.get("new"), 3)
        self.assertIsNone(cache.get("stale"))

    def test_read_refreshes_recency_but_not_the_deadline(self):
        clock = FakeClock()
        cache = TTLCache(maxsize=2, ttl=10, clock=clock)
        cache.set("a", 1)
        clock.advance(9)
        self.assertEqual(cache.get("a"), 1)   # recency touch, not a renewal
        clock.advance(2)                      # 11s since the write
        self.assertIsNone(cache.get("a"))

    def test_overwriting_a_key_renews_its_deadline(self):
        clock = FakeClock()
        cache = TTLCache(maxsize=2, ttl=10, clock=clock)
        cache.set("a", 1)
        clock.advance(9)
        cache.set("a", 2)
        clock.advance(5)
        self.assertEqual(cache.get("a"), 2)

    def test_expired_entries_never_evict_a_live_entry_under_pressure(self):
        clock = FakeClock()
        cache = TTLCache(maxsize=3, ttl=10, clock=clock)
        cache.set("x", 1)
        cache.set("y", 2)
        clock.advance(11)
        cache.set("live1", 3)
        cache.set("live2", 4)
        cache.set("live3", 5)
        self.assertEqual(
            [cache.get("live1"), cache.get("live2"), cache.get("live3")],
            [3, 4, 5],
        )


if __name__ == "__main__":
    unittest.main()
