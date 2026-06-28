import os

def load_context(context_dir: str) -> str:
    parts = []

    files = {
        "README.md": "README",
        "catalog.yaml": "Catalog",
        "CLAUDE.md": "Regras organizacionais",
        "CHANGELOG.md": "Changelog",
    }

    for filename, label in files.items():
        path = os.path.join(context_dir, filename)
        if os.path.exists(path):
            with open(path) as f:
                content = f.read().strip()
            parts.append(f"### {label}\n{content}")

    return "\n\n".join(parts)
