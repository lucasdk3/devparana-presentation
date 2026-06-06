import json


def format_as_comment(result: str, generic_result: str | None = None, title: str | None = None) -> str:
    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        heading = title or "AI Review"
        return f"## {heading}\n\n{result}"

    approved = data.get("approved", False)
    issues = data.get("issues", {})
    reason = data.get("reason", "")

    status_icon = "✅" if approved else "❌"
    status_label = "APROVADO" if approved else "REPROVADO"

    heading = title or "AI Review Structured"

    lines = [
        f"## {heading}",
        "",
        f"**Status:** {status_icon} {status_label}",
        "",
    ]

    if reason:
        lines += [f"> {reason}", ""]

    if approved and not any(issues.values() if isinstance(issues, dict) else issues):
        lines.append("Nenhum problema encontrado.")
        if generic_result:
            lines += ["", "---", "", _generic_section(generic_result)]
        return "\n".join(lines)

    agent_labels = {
        "qa": "QA",
        "tech-lead": "Tech Lead & Architect",
        "cyber-security": "Cyber Security",
        "product-manager": "Product Manager",
        "sre": "SRE",
    }

    if isinstance(issues, dict):
        for agent, agent_issues in issues.items():
            if not agent_issues:
                continue
            label = agent_labels.get(agent, agent.upper())
            lines += [f"### {label}", ""]
            for issue in agent_issues:
                lines.append(f"- {issue}")
            lines.append("")
    elif isinstance(issues, list):
        lines += ["### Problemas", ""]
        for issue in issues:
            lines.append(f"- {issue}")
        lines.append("")

    breaking = data.get("breaking_changes", [])
    if breaking:
        lines += ["### Breaking Changes", ""]
        for bc in breaking:
            lines.append(f"- ⚠️ {bc}")
        lines.append("")

    if generic_result:
        lines += ["---", "", _generic_section(generic_result)]

    lines += [
        "---",
        "",
        "_Gerado automaticamente por [reviewer-agent](https://github.com/lucasdk3/devparana-presentation)_",
    ]

    return "\n".join(lines)


def format_generic_as_comment(result: str) -> str:
    heading = "AI Review Generic"
    return "\n".join([
        f"## {heading}",
        "",
        result.strip(),
        "",
        "---",
        "",
        "_Gerado automaticamente por [reviewer-agent](https://github.com/lucasdk3/devparana-presentation)_",
    ])


def _generic_section(generic_result: str) -> str:
    return "\n".join([
        "<details>",
        "<summary>Review Genérico (sem contexto)</summary>",
        "",
        generic_result.strip(),
        "",
        "</details>",
    ])
