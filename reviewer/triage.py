import json
import re
import anthropic
from dataclasses import dataclass
from reviewer import config


# Mapping of conventional commit types to agents
_TYPE_AGENTS: dict[str, list[str]] = {
    "feat":     ["qa", "tech-lead"],
    "fix":      ["qa", "sre"],
    "perf":     ["sre", "qa"],
    "refactor": ["qa", "tech-lead"],
    "security": ["cyber-security", "qa"],
    "test":     ["qa"],
    "ci":       ["sre"],
    "build":    ["sre", "tech-lead"],
    "revert":   ["qa", "sre", "tech-lead"],
}

_TRIVIAL_TYPES = {"docs", "chore", "style", "typo"}

_BREAKING_AGENTS = ["qa", "tech-lead", "sre", "product-manager"]

_FORCE_GENERIC = "generic"
_FORCE_STRUCTURED = "structured"


@dataclass
class TriageResult:
    agents: list[str]
    mode: str          # "generic" | "structured" | "auto"
    source: str        # "pr-title" | "ai" | "trivial"
    reason: str


def parse_pr_title(title: str) -> TriageResult | None:
    """
    Parse a Conventional Commits PR title and return a TriageResult.
    Returns None if the title is not in conventional commit format
    (falls back to AI triage).

    Examples:
        review(generic): force generic mode
        review(structured): force structured mode
        feat(api)!: remove endpoint       → all breaking agents
        feat(api): add endpoint           → qa + tech-lead
        fix: token expired                → qa + sre
        security: hardcoded secret        → cyber-security + qa
        docs: update readme               → skip (trivial)
    """
    pattern = r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?\s*:\s*(?P<desc>.+)$"
    match = re.match(pattern, title.strip())

    if not match:
        return None

    commit_type = match.group("type")
    scope = match.group("scope") or ""
    is_breaking = match.group("breaking") == "!"

    # Explicit review mode overrides
    if commit_type == "review" and scope == _FORCE_GENERIC:
        return TriageResult(
            agents=[],
            mode=_FORCE_GENERIC,
            source="pr-title",
            reason=f"Modo genérico forçado pelo título do PR",
        )

    if commit_type == "review" and scope == _FORCE_STRUCTURED:
        return TriageResult(
            agents=[],
            mode=_FORCE_STRUCTURED,
            source="pr-title",
            reason=f"Modo estruturado forçado pelo título do PR",
        )

    # Breaking changes → all critical agents regardless of type
    if is_breaking:
        return TriageResult(
            agents=_BREAKING_AGENTS,
            mode="auto",
            source="pr-title",
            reason=f"Breaking change detectado ({commit_type}!): acionando todos os agentes críticos",
        )

    # Trivial types → skip review
    if commit_type in _TRIVIAL_TYPES:
        return TriageResult(
            agents=[],
            mode="auto",
            source="trivial",
            reason=f"Tipo '{commit_type}' considerado trivial pelo conventional commit",
        )

    # Known types → deterministic agent mapping
    if commit_type in _TYPE_AGENTS:
        agents = _TYPE_AGENTS[commit_type]
        return TriageResult(
            agents=agents,
            mode="auto",
            source="pr-title",
            reason=f"Tipo '{commit_type}' mapeado para agentes: {', '.join(agents)}",
        )

    # Unknown type → fall back to AI triage
    return None


def run_triage(diff: str, pr_title: str | None = None) -> TriageResult:
    """
    Run triage to determine which agents should be invoked.

    If pr_title is provided and matches conventional commit format,
    uses deterministic mapping (no AI call). Otherwise falls back to AI.
    """
    if pr_title:
        result = parse_pr_title(pr_title)
        if result is not None:
            return result

    # AI-based triage
    prompt_template = open(".claude/prompts/triage.md").read()
    client = anthropic.Anthropic()

    create_kwargs: dict = dict(
        model=config.MODEL,
        max_tokens=config.TRIAGE_MAX_TOKENS,
        messages=[{"role": "user", "content": f"{prompt_template}\n\n{diff}"}],
    )
    if config.TEMPERATURE is not None:
        create_kwargs["temperature"] = config.TEMPERATURE

    response = client.messages.create(**create_kwargs)

    raw = response.content[0].text.strip()
    data = json.loads(raw)
    return TriageResult(
        agents=data.get("agents", []),
        mode="auto",
        source="ai",
        reason=data.get("reason", ""),
    )
