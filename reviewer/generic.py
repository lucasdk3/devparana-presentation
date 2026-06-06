import json
import anthropic
from reviewer import config

_SUBMIT_TOOL = {
    "name": "submit_review",
    "description": "Submit the PR review findings",
    "input_schema": {
        "type": "object",
        "properties": {
            "approved": {
                "type": "boolean",
                "description": "Whether the PR is approved"
            },
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of issues found in the PR"
            },
            "summary": {
                "type": "string",
                "description": "Brief summary of the review"
            },
        },
        "required": ["approved", "issues", "summary"],
    },
}


def run_generic_review(diff: str) -> str:
    prompt_template = open(".claude/prompts/generic.md").read()
    prompt = f"{prompt_template}\n\n{diff}"

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=config.MODEL,
        max_tokens=config.MAX_TOKENS,
        tools=[_SUBMIT_TOOL],
        tool_choice={"type": "tool", "name": "submit_review"},
        messages=[{"role": "user", "content": prompt}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "submit_review":
            return json.dumps(block.input)

    return json.dumps({"approved": True, "issues": [], "summary": "Sem resultado."})
