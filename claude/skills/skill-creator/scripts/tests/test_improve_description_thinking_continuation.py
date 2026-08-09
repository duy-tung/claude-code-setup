"""Tests for preserving thinking blocks across description rewrites."""

import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


try:
    import anthropic  # noqa: F401
except ModuleNotFoundError:
    anthropic_stub = types.ModuleType("anthropic")
    anthropic_stub.Anthropic = object
    sys.modules["anthropic"] = anthropic_stub

SKILL_CREATOR_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_CREATOR_DIR))

from scripts.improve_description import improve_description


class ImproveDescriptionThinkingContinuationTest(unittest.TestCase):
    def test_rewrite_reuses_complete_assistant_content(self):
        long_description = "x" * 1025
        thinking_block = SimpleNamespace(
            type="thinking",
            thinking="summary of private reasoning",
            signature="signed-thinking",
        )
        redacted_thinking_block = SimpleNamespace(
            type="redacted_thinking",
            data="opaque-redacted-thinking",
        )
        text_block = SimpleNamespace(
            type="text",
            text=f"<new_description>{long_description}</new_description>",
        )
        original_content = [thinking_block, redacted_thinking_block, text_block]

        client = Mock()
        client.messages.create.side_effect = [
            SimpleNamespace(content=original_content),
            SimpleNamespace(
                content=[
                    SimpleNamespace(
                        type="text",
                        text="<new_description>Short description.</new_description>",
                    )
                ]
            ),
        ]

        result = improve_description(
            client=client,
            skill_name="example-skill",
            skill_content="Example skill instructions.",
            current_description="Current description.",
            eval_results={
                "results": [],
                "summary": {"passed": 0, "total": 0},
            },
            history=[],
            model="claude-opus-5",
        )

        self.assertEqual(result, "Short description.")
        self.assertEqual(client.messages.create.call_count, 2)

        second_request = client.messages.create.call_args_list[1]
        assistant_message = second_request.kwargs["messages"][1]

        self.assertEqual(assistant_message["role"], "assistant")
        self.assertIs(assistant_message["content"], original_content)
        self.assertEqual(
            [block.type for block in assistant_message["content"]],
            ["thinking", "redacted_thinking", "text"],
        )
        self.assertIs(assistant_message["content"][0], thinking_block)
        self.assertIs(assistant_message["content"][1], redacted_thinking_block)
        self.assertIs(assistant_message["content"][2], text_block)
        self.assertNotEqual(assistant_message["content"], text_block.text)

    def test_older_model_omits_adaptive_thinking_request(self):
        client = Mock()
        client.messages.create.return_value = SimpleNamespace(
            content=[
                SimpleNamespace(
                    type="text",
                    text="<new_description>Compatible description.</new_description>",
                )
            ]
        )

        result = improve_description(
            client=client,
            skill_name="example-skill",
            skill_content="Example skill instructions.",
            current_description="Current description.",
            eval_results={
                "results": [],
                "summary": {"passed": 0, "total": 0},
            },
            history=[],
            model="claude-haiku-4-5",
        )

        self.assertEqual(result, "Compatible description.")
        self.assertNotIn("thinking", client.messages.create.call_args.kwargs)

    def test_initial_refusal_discards_partial_description(self):
        client = Mock()
        client.messages.create.return_value = SimpleNamespace(
            stop_reason="refusal",
            content=[
                SimpleNamespace(
                    type="text",
                    text="<new_description>PARTIAL REFUSED OUTPUT</new_description>",
                )
            ],
        )

        with self.assertRaisesRegex(RuntimeError, "partial response was discarded"):
            improve_description(
                client=client,
                skill_name="example-skill",
                skill_content="Example skill instructions.",
                current_description="Current description.",
                eval_results={
                    "results": [],
                    "summary": {"passed": 0, "total": 0},
                },
                history=[],
                model="claude-opus-5",
            )

    def test_rewrite_refusal_discards_partial_description(self):
        long_description = "x" * 1025
        client = Mock()
        client.messages.create.side_effect = [
            SimpleNamespace(
                stop_reason="end_turn",
                content=[
                    SimpleNamespace(
                        type="text",
                        text=(
                            "<new_description>"
                            + long_description
                            + "</new_description>"
                        ),
                    )
                ],
            ),
            SimpleNamespace(
                stop_reason="refusal",
                content=[
                    SimpleNamespace(
                        type="text",
                        text="<new_description>PARTIAL REFUSED OUTPUT</new_description>",
                    )
                ],
            ),
        ]

        with self.assertRaisesRegex(RuntimeError, "description shortening"):
            improve_description(
                client=client,
                skill_name="example-skill",
                skill_content="Example skill instructions.",
                current_description="Current description.",
                eval_results={
                    "results": [],
                    "summary": {"passed": 0, "total": 0},
                },
                history=[],
                model="claude-opus-5",
            )


if __name__ == "__main__":
    unittest.main()
