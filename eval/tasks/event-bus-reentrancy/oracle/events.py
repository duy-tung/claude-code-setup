"""A minimal synchronous event bus with FIFO re-entrant dispatch."""


class EventBus:
    def __init__(self):
        self._handlers = {}
        self._queue = []
        self._dispatching = False

    def subscribe(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)
        return handler

    def unsubscribe(self, event, handler):
        handlers = self._handlers.get(event)
        if handlers and handler in handlers:
            handlers.remove(handler)

    def once(self, event, handler):
        def wrapper(payload=None):
            # Detach before invoking so a nested publish cannot re-enter it.
            self.unsubscribe(event, wrapper)
            handler(payload)

        self.subscribe(event, wrapper)
        return wrapper

    def publish(self, event, payload=None):
        # Queue first: a publish from inside a handler is delivered after the
        # current dispatch drains, not nested inside it.
        self._queue.append((event, payload))
        if self._dispatching:
            return
        self._dispatching = True
        try:
            while self._queue:
                current_event, current_payload = self._queue.pop(0)
                # Snapshot so subscribing during dispatch does not extend this
                # pass, and re-check membership so unsubscribing during dispatch
                # takes effect immediately.
                for handler in list(self._handlers.get(current_event, [])):
                    if handler in self._handlers.get(current_event, []):
                        handler(current_payload)
        finally:
            self._dispatching = False
