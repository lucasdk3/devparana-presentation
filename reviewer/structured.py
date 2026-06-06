import json
import anthropic
from reviewer.triage import run_triage
from reviewer.context import load_context
from reviewer import config

SKILL_KEYS = ["qa", "tech-lead", "cyber-security", "product-manager", "sre"]

_SUBMIT_TOOL = {
    "name": "submit_review",
    "description": "Submit the structured PR review findings from all agent perspectives",
    "input_schema": {
        "type": "object",
        "properties": {
            "approved": {
                "type": "boolean",
                "description": "Whether the PR is approved overall"
            },
            "issues": {
                "type": "object",
                "description": "Issues per agent (qa, tech-lead, cyber-security, product-manager, sre)",
                "additionalProperties": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "reason": {
                "type": "string",
                "description": "Overall justification for the approval or rejection"
            },
            "breaking_changes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of breaking changes detected, if any"
            },
        },
        "required": ["approved", "issues", "reason"],
    },
}


def load_skill(skill_name: str) -> str:
    path = f".claude/skills/{skill_name}/SKILL.md"
    with open(path) as f:
        return f.read()


def build_structured_prompt(diff: str, context: str, agents: list[str]) -> str:
    template = open(".claude/prompts/structured.md").read()
    prompt_with_context = template.replace("{context}", context)

    skills_section = ""
    for agent in agents:
        try:
            skill = load_skill(agent)
            skills_section += f"\n\n---\n## Skill: {agent}\n{skill}"
        except FileNotFoundError:
            pass

    return f"{prompt_with_context}{skills_section}\n\n## Diff do Pull Request\n{diff}"


def run_structured_review(diff: str, context_dir: str = "app-example", pr_title: str | None = None) -> str:
    triage = run_triage(diff, pr_title=pr_title)

    if not triage.agents:
        return json.dumps({"approved": True, "issues": {}, "reason": "Mudança trivial.", "breaking_changes": []})

    context = load_context(context_dir)
    prompt = build_structured_prompt(diff, context, triage.agents)

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

    return json.dumps({"approved": True, "issues": {}, "reason": "Sem resultado.", "breaking_changes": []})
