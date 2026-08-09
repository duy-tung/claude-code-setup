"""A minimal synchronous event bus."""


class EventBus:
    def __init__(self):
        self._handlers = {}

    def subscribe(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)
        return handler

    def unsubscribe(self, event, handler):
        handlers = self._handlers.get(event)
        if handlers and handler in handlers:
            handlers.remove(handler)

    def publish(self, event, payload=None):
        for handler in self._handlers.get(event, []):
            handler(payload)
