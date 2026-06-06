import anyio
import json
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from reviewer.triage import run_triage
from reviewer.context import load_context
from reviewer import config

SKILL_KEYS = ["qa", "tech-lead", "cyber-security", "product-manager", "sre"]

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

async def run_structured_review(diff: str, context_dir: str = "app-example", pr_title: str | None = None) -> str:
    triage = run_triage(diff, pr_title=pr_title)

    if not triage.agents:
        return '{"approved": true, "issues": {}, "reason": "Mudança trivial."}'

    context = load_context(context_dir)
    prompt = build_structured_prompt(diff, context, triage.agents)

    options = ClaudeAgentOptions(
        model=config.MODEL,
        allowed_tools=[],
        **({"max_budget_usd": config.MAX_BUDGET_USD} if config.MAX_BUDGET_USD is not None else {}),
    )

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            return message.result

    return ""
