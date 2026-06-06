import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from reviewer import config


async def run_generic_review(diff: str) -> str:
    prompt_template = open(".claude/prompts/generic.md").read()
    prompt = f"{prompt_template}\n\n{diff}"

    options = ClaudeAgentOptions(
        model=config.MODEL,
        allowed_tools=[],
        **({"temperature": config.TEMPERATURE} if config.TEMPERATURE is not None else {}),
        **({"max_tokens": config.MAX_TOKENS} if config.MAX_TOKENS is not None else {}),
    )

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            return message.result

    return ""
