import unittest

from events import EventBus


class TestEventBus(unittest.TestCase):
    def test_subscribe_and_publish(self):
        bus = EventBus()
        seen = []
        bus.subscribe("tick", seen.append)
        bus.publish("tick", 1)
        self.assertEqual(seen, [1])

    def test_unsubscribe_stops_delivery(self):
        bus = EventBus()
        seen = []
        handler = bus.subscribe("tick", seen.append)
        bus.unsubscribe("tick", handler)
        bus.publish("tick", 1)
        self.assertEqual(seen, [])

    def test_publish_to_unknown_event_is_noop(self):
        EventBus().publish("nobody-listens", 1)

    def test_once_fires_a_single_time(self):
        bus = EventBus()
        seen = []
        bus.once("tick", seen.append)
        bus.publish("tick", 1)
        bus.publish("tick", 2)
        self.assertEqual(seen, [1])
