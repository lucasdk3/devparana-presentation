# reviewer-agent

Projeto de demonstração para palestras sobre **Prompt Engineering**, **Context Engineering** e **Automação de Validação de Software com IA**.

Apresentado no [DevParaná](https://devparana.org).

---

## Mensagem principal

> *"IA não substitui conhecimento de engenharia. Ela amplifica conhecimento estruturado."*

O modelo não mudou. O código não mudou. **O que mudou foi o contexto e a especialização.**

---

## O que este projeto demonstra

Dois pipelines de review de Pull Request rodando sobre o mesmo diff:

| | Pipeline Genérica | Pipeline Estruturada |
|---|---|---|
| **Entrada** | Git diff | Git diff + README + catalog.yaml + CLAUDE.md + migration-guide.yaml |
| **Prompt** | Simples, sem contexto | Estruturado com 5 perspectivas especializadas |
| **Agentes** | Nenhum | QA, Tech Lead, Cyber Security, Product Manager, SRE |
| **Resultado** | Poucos problemas, baixa precisão | Mais problemas, contexto de negócio, especialização |

---

## Estrutura do projeto

```
reviewer-agent/
│
├── app-example/                  # Aplicação-alvo do review (FastAPI)
│   ├── main.py
│   ├── handlers/framework.py
│   ├── models/framework.py
│   ├── tests/test_framework.py
│   ├── docs/swagger.json
│   ├── README.md                 # Contexto: como rodar, variáveis, endpoints
│   ├── CLAUDE.md                 # Contexto: regras organizacionais
│   ├── catalog.yaml              # Contexto: catálogo do serviço (Backstage)
│   └── migration-guide.yaml      # Contexto: breaking changes registrados
│
├── reviewer/                     # Pacote Python do agente
│   ├── cli.py                    # Interface de linha de comando (Typer)
│   ├── generic.py                # Pipeline genérica (prompt simples)
│   ├── structured.py             # Pipeline estruturada (context + skills)
│   ├── triage.py                 # Triagem: conventional commits + IA
│   ├── context.py                # Carrega arquivos de contexto
│   ├── reports.py                # Relatório comparativo
│   └── github.py                 # Formata resultado como comentário de PR
│
├── .claude/
│   ├── prompts/
│   │   ├── generic.md            # Prompt simples
│   │   ├── structured.md         # Prompt estruturado com 5 perspectivas
│   │   └── triage.md             # Prompt de triagem via IA
│   ├── skills/
│   │   ├── qa/SKILL.md
│   │   ├── tech-lead/SKILL.md
│   │   ├── cyber-security/SKILL.md
│   │   ├── product-manager/SKILL.md
│   │   ├── sre/SKILL.md
│   │   └── approval/SKILL.md
│   └── examples/
│       ├── good-pr.diff
│       ├── bad-pr.diff           # Segredo hardcoded + sem testes + sem swagger
│       └── breaking-change.diff  # JWT_SECRET renomeado para AUTH_SECRET
│
├── tests/
│   └── skills/                   # Testes com promptfoo
│       ├── promptfooconfig.yaml
│       ├── triage.yaml
│       ├── qa.yaml
│       ├── tech-lead.yaml
│       ├── cyber-security.yaml
│       ├── product-manager.yaml
│       ├── sre.yaml
│       └── approval.yaml
│
├── .github/
│   └── workflows/
│       └── ai-review.yml         # Pipeline GitHub Actions
│
├── pyproject.toml
└── requirements.txt
```

---

## Pré-requisitos

- Python >= 3.10
- Chave de API da Anthropic

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Como usar

### Review genérico

Prompt simples, sem contexto, sem especialização.

```bash
python -m reviewer review generic --diff .claude/examples/bad-pr.diff
```

### Review estruturado

Contexto completo do serviço + 5 agentes especializados.

```bash
python -m reviewer review structured \
  --diff .claude/examples/bad-pr.diff \
  --context-dir app-example
```

### Comparação lado a lado

Roda os dois e exibe o relatório comparativo.

```bash
python -m reviewer review compare \
  --diff .claude/examples/bad-pr.diff \
  --context-dir app-example
```

### Triagem

Verifica quais agentes devem ser acionados para um dado diff.

```bash
# Só pelo diff (usa IA)
python -m reviewer triage --diff .claude/examples/bad-pr.diff

# Com título de PR (Conventional Commits — sem chamar IA para tipos conhecidos)
python -m reviewer triage \
  --diff .claude/examples/bad-pr.diff \
  --pr-title "feat(api): add details endpoint"
```

### Formatar comentário de PR

Converte o JSON do review estruturado em markdown pronto para o GitHub.

```bash
python -m reviewer review structured \
  --diff .claude/examples/bad-pr.diff \
  --format github
```

---

## Triagem inteligente com Conventional Commits

Quando o título do PR segue o padrão [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), a triagem é **determinística** — sem custo de tokens.

| Título do PR | Agentes acionados |
|---|---|
| `feat: add endpoint` | qa, tech-lead |
| `fix: token expired` | qa, sre |
| `perf: slow query` | sre, qa |
| `refactor: extract service` | qa, tech-lead |
| `security: validate input` | cyber-security, qa |
| `ci: update pipeline` | sre |
| `feat(api)!: remove endpoint` | qa, tech-lead, sre, product-manager |
| `docs: update readme` | — (trivial, skip) |
| `chore: bump deps` | — (trivial, skip) |
| `review(generic): force mode` | força pipeline genérica |
| `review(structured): force mode` | força pipeline estruturada |
| título sem padrão | triagem via IA |

---

## Agentes especializados

| Agente | Responsabilidade |
|---|---|
| **QA** | Testes, regressão, cobertura |
| **Tech Lead** | Swagger, README, boas práticas, breaking changes estruturais |
| **Cyber Security** | Segredos hardcoded, autenticação, exposição de dados |
| **Product Manager** | Impacto ao usuário, remoção de comportamentos, comunicação |
| **SRE** | Risco de deploy, variáveis de ambiente, observabilidade |
| **Approval** | Decisão final consolidada |

---

## Cenários de demonstração

### Cenário 1 — PR ruim (`bad-pr.diff`)

Contém:
- Novo endpoint sem teste
- Swagger não atualizado
- Segredo hardcoded (`AUTH_SECRET = "hardcoded-secret-123"`)

### Cenário 2 — Breaking change (`breaking-change.diff`)

Contém:
- `JWT_SECRET` renomeado para `AUTH_SECRET`
- Endpoint `GET /frameworks/{id}` removido
- Migration guide não atualizado

### Cenário 3 — PR bom (`good-pr.diff`)

Contém apenas:
- Adição de logger
- Novo teste

---

## GitHub Actions

A pipeline roda automaticamente em PRs que tocam `app-example/**`.

```
PR aberto
    │
    ▼
[triage]  →  lê título do PR (Conventional Commits)
    │         se tipo conhecido → determinístico (sem IA)
    │         se desconhecido   → triagem via IA
    │
    ├── trivial ──────────────► [skip-review] → comenta "aprovado automaticamente"
    │
    └── não trivial
            │
            ├── [generic-review]    ─┐
            └── [structured-review] ─┴► [post-comment] → [enforce]
```

### Comentários de PR

O agente posta comentários diferenciados conforme o modo:

| Modo | Título do comentário |
|---|---|
| `generic` | `## AI Review Generic` |
| `structured` | `## AI Review Structured` |
| `auto` | `## AI Review Structured` (com genérico colapsado dentro) |

O comentário é atualizado a cada push — não duplicado.

### AI Review Gate

O job **AI Review Gate** faz `exit 1` quando o review estruturado retorna `approved: false`, bloqueando o merge.

Para ativar como check obrigatório:

> _Settings → Branches → Branch protection rules → main → Require status checks → `AI Review Gate`_

### Variáveis configuráveis no repositório

| Variável (`vars.*`) | Padrão | Descrição |
|---|---|---|
| `REVIEWER_MODEL` | `claude-haiku-4-5-20251001` | Modelo usado em todas as chamadas |
| `REVIEWER_MAX_BUDGET_USD` | sem limite | Limite de custo em USD por chamada ao agente |
| `REVIEWER_TRIAGE_MAX_TOKENS` | `256` | Limite de tokens para a triagem via IA |

**Secret necessário no repositório:**

```
ANTHROPIC_API_KEY
```

---

## Testes de skills com promptfoo

Valida cada skill isoladamente, sem depender da execução completa do pipeline.

```bash
# Instalar
npm install -g promptfoo

# Rodar todos os testes
promptfoo eval --config tests/skills/promptfooconfig.yaml

# Rodar uma skill específica
promptfoo eval --config tests/skills/qa.yaml

# Ver resultado no browser
promptfoo view
```

---

## Tecnologias

| Tecnologia | Uso |
|---|---|
| [Claude Haiku 4.5](https://www.anthropic.com) | Modelo de IA (todas as chamadas) |
| [Claude Agent SDK](https://github.com/anthropics/claude-code) | Pipeline genérica e estruturada |
| [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) | Triagem (chamada direta) |
| [FastAPI](https://fastapi.tiangolo.com) | Aplicação de exemplo |
| [Typer](https://typer.tiangolo.com) | CLI |
| [promptfoo](https://www.promptfoo.dev) | Testes de prompts |
| [GitHub Actions](https://docs.github.com/en/actions) | Pipeline CI/CD |

---

## Licença

MIT
