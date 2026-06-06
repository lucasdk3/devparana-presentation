# CLAUDE.md — reviewer-agent

Instruções para o Claude Code ao trabalhar neste repositório.

---

## Visão geral do projeto

Este é um projeto de **demonstração educacional** para palestras sobre IA aplicada ao desenvolvimento de software.

Objetivo: mostrar a diferença entre uma análise genérica e uma análise estruturada de Pull Requests usando o Claude Agent SDK.

Não é uma ferramenta enterprise. Não substitui SonarQube, Trivy ou Semgrep. É material de palestra.

---

## Estrutura e responsabilidades

### `reviewer/` — Pacote principal

| Arquivo | Responsabilidade |
|---|---|
| `cli.py` | Ponto de entrada via Typer. Comandos: `triage`, `review generic`, `review structured`, `review compare`, `format` |
| `triage.py` | Decide quais agentes acionar. Primeiro tenta Conventional Commits (determinístico), depois cai na IA |
| `generic.py` | Executa review com prompt simples via Agent SDK |
| `structured.py` | Executa review estruturado: carrega contexto + skills dos agentes acionados pela triagem |
| `context.py` | Lê `README.md`, `catalog.yaml`, `CLAUDE.md`, `migration-guide.yaml` do diretório alvo |
| `github.py` | Formata o JSON de resultado em markdown para comentário de PR |
| `reports.py` | Relatório comparativo entre generic e structured no terminal |

### `.claude/` — Assets de IA

```
.claude/
├── prompts/          # Prompts usados pelo reviewer
│   ├── generic.md    # Prompt simples (sem contexto)
│   ├── structured.md # Prompt estruturado (5 perspectivas)
│   └── triage.md     # Prompt de triagem via IA
├── skills/           # Uma skill por agente especializado
│   ├── qa/
│   ├── tech-lead/
│   ├── cyber-security/
│   ├── product-manager/
│   ├── sre/
│   └── approval/
└── examples/         # Diffs prontos para demo
    ├── good-pr.diff
    ├── bad-pr.diff
    └── breaking-change.diff
```

### `app-example/` — Aplicação-alvo

FastAPI simples sobre frameworks de Prompt Engineering. Serve como alvo dos reviews de demonstração. Os arquivos `README.md`, `CLAUDE.md`, `catalog.yaml` e `migration-guide.yaml` dentro dela são os **arquivos de contexto** injetados no review estruturado.

---

## Modelo usado

```
claude-haiku-4-5-20251001
```

Usar este modelo em todas as chamadas. Não substituir por modelos mais caros sem necessidade — este é um projeto de demo com foco em custo-benefício.

---

## Convenções do projeto

### Conventional Commits

Todos os commits neste repositório devem seguir Conventional Commits:

```
feat: nova funcionalidade
fix: correção de bug
docs: documentação
refactor: refatoração sem mudança de comportamento
test: adição ou correção de testes
chore: tarefas de manutenção
```

Breaking changes: adicionar `!` antes dos dois-pontos: `feat!: remove endpoint`

### Testes

Ao modificar qualquer skill em `.claude/skills/`, verificar se os testes correspondentes em `tests/skills/` ainda passam:

```bash
promptfoo eval --config tests/skills/promptfooconfig.yaml
```

### Paths relativos

O reviewer é executado a partir da **raiz do repositório**. Todos os `open()` usam paths relativos à raiz:

```python
open(".claude/prompts/triage.md")     # correto
open(".claude/skills/qa/SKILL.md")    # correto
open("prompts/triage.md")             # errado
```

---

## Fluxo da triagem

A triagem tem dois caminhos:

1. **Determinístico** (Conventional Commits no título do PR): sem chamada à IA, sem custo de tokens.
2. **IA** (título sem padrão ou tipo desconhecido): chama `claude-haiku` com `.claude/prompts/triage.md`.

Mapeamento de tipos para agentes (definido em `triage.py`):

| Tipo | Agentes |
|---|---|
| `feat` | qa, tech-lead |
| `fix` | qa, sre |
| `perf` | sre, qa |
| `refactor` | qa, tech-lead |
| `security` | cyber-security, qa |
| `test` | qa |
| `ci` | sre |
| `build` | sre, tech-lead |
| `revert` | qa, sre, tech-lead |
| `docs`, `chore`, `style`, `typo` | — (trivial, skip) |
| qualquer tipo com `!` | qa, tech-lead, sre, product-manager |

---

## O que NÃO fazer

- Não adicionar complexidade desnecessária. O propósito é ser claro e didático para uma palestra.
- Não usar subagentes reais (múltiplos processos Agent SDK em paralelo). A especialização é feita via **estrutura do prompt** e **skills carregadas**.
- Não trocar o modelo por padrão. O ponto da demo é que o **contexto** faz diferença, não o modelo.
- Não mover `prompts/` ou `examples/` para fora de `.claude/`. A convenção é manter assets de IA dentro de `.claude/`.
- Não criar abstrações prematuras. Três linhas similares são melhores que uma abstração desnecessária.

---

## Variáveis de ambiente

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Sim | — | Chave da API Anthropic |
| `REVIEWER_MODEL` | Não | `claude-haiku-4-5-20251001` | Modelo usado em todas as chamadas |
| `REVIEWER_TEMPERATURE` | Não | padrão do modelo | Temperatura (0.0 = determinístico, 1.0 = padrão Claude) |
| `REVIEWER_MAX_TOKENS` | Não | sem limite | Limite de tokens para respostas dos agentes |
| `REVIEWER_TRIAGE_MAX_TOKENS` | Não | `256` | Limite de tokens para a triagem via IA |

A configuração é centralizada em `reviewer/config.py` e lida uma vez no import.

---

## Como rodar localmente para testar

```bash
# Review genérico no cenário ruim
python -m reviewer review generic --diff .claude/examples/bad-pr.diff

# Review estruturado com contexto
python -m reviewer review structured \
  --diff .claude/examples/bad-pr.diff \
  --context-dir app-example

# Comparação completa
python -m reviewer review compare \
  --diff .claude/examples/bad-pr.diff \
  --context-dir app-example

# Triagem com título de PR
python -m reviewer triage \
  --diff .claude/examples/bad-pr.diff \
  --pr-title "feat(api): add details endpoint"

# Testes de skills
promptfoo eval --config tests/skills/promptfooconfig.yaml
```
