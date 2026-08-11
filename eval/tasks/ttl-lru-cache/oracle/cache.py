"""An LRU cache with a per-entry time-to-live."""
import time


class TTLCache:
    def __init__(self, maxsize=128, ttl=60.0, clock=time.monotonic):
        self.maxsize = maxsize
        self.ttl = ttl
        self._clock = clock
        self._data = {}   # key -> (value, expires_at)
        self._order = []  # LRU order, oldest first

    def _is_expired(self, key):
        return self._data[key][1] <= self._clock()

    def _drop(self, key):
        self._data.pop(key, None)
        if key in self._order:
            self._order.remove(key)

    def _purge_expired(self):
        for key in [k for k in self._order if self._is_expired(k)]:
            self._drop(key)

    def get(self, key, default=None):
        if key not in self._data:
            return default
        if self._is_expired(key):
            self._drop(key)
            return default
        value, _ = self._data[key]
        # Recency moves; the expiry deadline does not.
        self._order.remove(key)
        self._order.append(key)
        return value

    def set(self, key, value):
        if key in self._data:
            self._order.remove(key)
        else:
            if len(self._data) >= self.maxsize:
                # Reclaim dead entries before sacrificing a live one.
                self._purge_expired()
            if len(self._data) >= self.maxsize:
                self._drop(self._order[0])
        self._data[key] = (value, self._clock() + self.ttl)
        self._order.append(key)

    def __len__(self):
        self._purge_expired()
        return len(self._data)
