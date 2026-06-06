import json

def count_issues(result: str) -> int:
    try:
        data = json.loads(result)
        if "issues" in data and isinstance(data["issues"], dict):
            return sum(len(v) for v in data["issues"].values())
        return 0
    except Exception:
        lines = [l.strip() for l in result.strip().splitlines() if l.strip().startswith("-")]
        return len(lines)

def print_comparison(generic_result: str, structured_result: str) -> None:
    generic_count = count_issues(generic_result)
    structured_count = count_issues(structured_result)

    print("=" * 26)
    print("COMPARAÇÃO")
    print("=" * 26)
    print()
    print("Prompt Genérico")
    print()
    print(f"Problemas encontrados: {generic_count}")
    print()
    print("Tokens: N/A")
    print()
    print("-" * 26)
    print()
    print("Prompt Estruturado")
    print()
    print(f"Problemas encontrados: {structured_count}")
    print()
    print("Tokens: N/A")
    print()
    print("-" * 26)
    print()
    if generic_count > 0 and structured_count > generic_count:
        pct = int(((structured_count - generic_count) / generic_count) * 100)
        print(f"Diferença: +{pct}% mais problemas relevantes detectados")
    elif structured_count > generic_count:
        print(f"Diferença: +{structured_count - generic_count} problemas adicionais detectados")
    else:
        print("Diferença: Resultados similares")
    print()
