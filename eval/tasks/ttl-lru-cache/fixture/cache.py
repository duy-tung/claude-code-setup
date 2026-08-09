"""An LRU cache with a per-entry time-to-live."""
import time


class TTLCache:
    def __init__(self, maxsize=128, ttl=60.0, clock=time.monotonic):
        self.maxsize = maxsize
        self.ttl = ttl
        self._clock = clock
        self._data = {}   # key -> (value, expires_at)
        self._order = []  # LRU order, oldest first

    def get(self, key, default=None):
        if key not in self._data:
            return default
        value, expires_at = self._data[key]
        self._order.remove(key)
        self._order.append(key)
        return value

    def set(self, key, value):
        if key in self._data:
            self._order.remove(key)
        elif len(self._data) >= self.maxsize:
            oldest = self._order.pop(0)
            del self._data[oldest]
        self._data[key] = (value, self._clock() + self.ttl)
        self._order.append(key)

    def __len__(self):
        return len(self._data)
