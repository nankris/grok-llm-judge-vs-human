"""Judge prompts. The model sees policy and the question/reply, never labels."""

from __future__ import annotations

FULL_INSTRUCTIONS = """You are grading one support-bot reply for a fictional bike shop.

Do not use tools. Do not browse. Do not read files. Do not call subagents. The policy and rubric in this message are the only rules. Decide PASS or FAIL yourself.

Reply with one JSON object and nothing else, in this shape:
{"verdict":"PASS","reason":"one or two sentences"}
or
{"verdict":"FAIL","reason":"one or two sentences"}
The verdict must be exactly PASS or FAIL. Do not output a category field.
"""

MINIMAL_INSTRUCTIONS = """You grade one bike-shop support reply.

Do not use tools. Do not browse. Do not read files. Do not call subagents.

Is this reply good? PASS or FAIL.

Reply with one JSON object and nothing else:
{"verdict":"PASS","reason":"one or two sentences"}
or
{"verdict":"FAIL","reason":"one or two sentences"}
"""


def build_prompt(config: str, policy: str, rubric: str, question: str, reply: str) -> str:
    if config == "full":
        return (
            FULL_INSTRUCTIONS
            + "\n## Policy\n"
            + policy.strip()
            + "\n\n## Rubric\n"
            + rubric.strip()
            + "\n\n## Customer question\n"
            + question.strip()
            + "\n\n## Bot reply\n"
            + reply.strip()
            + "\n"
        )
    if config == "minimal":
        return (
            MINIMAL_INSTRUCTIONS
            + "\nPolicy:\n"
            + policy.strip()
            + "\n\nCustomer question:\n"
            + question.strip()
            + "\n\nBot reply:\n"
            + reply.strip()
            + "\n"
        )
    raise ValueError(config)


JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
        "reason": {"type": "string"},
    },
    "required": ["verdict", "reason"],
    "additionalProperties": False,
}
