"""Hidden dispatch-semantics contract for the event bus."""
import sys
import unittest

from events import EventBus


class TestDispatchSemantics(unittest.TestCase):
    def test_unsubscribe_during_dispatch_skips_only_that_handler(self):
        bus = EventBus()
        seen = []

        def first(payload):
            seen.append("first")
            bus.unsubscribe("tick", second)

        def second(payload):
            seen.append("second")

        def third(payload):
            seen.append("third")

        bus.subscribe("tick", first)
        bus.subscribe("tick", second)
        bus.subscribe("tick", third)
        bus.publish("tick", None)

        # second was detached mid-dispatch, third must still run.
        self.assertEqual(seen, ["first", "third"])

    def test_subscribing_during_dispatch_waits_for_the_next_publish(self):
        bus = EventBus()
        seen = []
        bus.subscribe("tick", lambda p: bus.subscribe("tick", lambda q: seen.append("late")))
        bus.publish("tick", None)
        self.assertEqual(seen, [])
        bus.publish("tick", None)
        self.assertIn("late", seen)

    def test_nested_publish_is_queued_fifo_not_recursive(self):
        bus = EventBus()
        order = []

        def on_a(payload):
            order.append("a-start")
            bus.publish("b", None)
            order.append("a-end")

        bus.subscribe("a", on_a)
        bus.subscribe("b", lambda p: order.append("b"))
        bus.publish("a", None)

        # "b" must not interrupt the "a" dispatch.
        self.assertEqual(order, ["a-start", "a-end", "b"])

    def test_deep_chain_does_not_grow_the_python_stack(self):
        bus = EventBus()
        depths = []
        remaining = {"n": 200}

        def on_tick(payload):
            depths.append(len(traceback_frames()))
            if remaining["n"] > 0:
                remaining["n"] -= 1
                bus.publish("tick", None)

        def traceback_frames():
            frames, frame = [], sys._getframe()
            while frame is not None:
                frames.append(frame)
                frame = frame.f_back
            return frames

        bus.subscribe("tick", on_tick)
        bus.publish("tick", None)

        self.assertEqual(remaining["n"], 0)
        # Queued dispatch keeps every delivery at the same stack depth.
        self.assertEqual(len(set(depths)), 1, f"stack depth grew: {sorted(set(depths))}")

    def test_once_survives_a_nested_publish_of_the_same_event(self):
        bus = EventBus()
        seen = []

        def handler(payload):
            seen.append(payload)
            bus.publish("tick", "nested")

        bus.once("tick", handler)
        bus.publish("tick", "first")
        self.assertEqual(seen, ["first"])

    def test_once_and_regular_handlers_coexist(self):
        bus = EventBus()
        seen = []
        bus.once("tick", lambda p: seen.append(("once", p)))
        bus.subscribe("tick", lambda p: seen.append(("always", p)))
        bus.publish("tick", 1)
        bus.publish("tick", 2)
        self.assertEqual(seen, [("once", 1), ("always", 1), ("always", 2)])


if __name__ == "__main__":
    unittest.main()
