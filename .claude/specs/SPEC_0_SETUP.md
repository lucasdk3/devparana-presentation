# SPEC - AI Pull Request Reviewer Demo

## Objetivo

Criar um projeto open source para demonstração em palestras sobre:

* Prompt Engineering
* Context Engineering
* Agentes Especializados
* Automação de Validação de Software com IA

O projeto deve demonstrar claramente a diferença entre:

1. Uma análise genérica utilizando apenas um prompt simples.
2. Uma análise estruturada utilizando contexto, regras e especialização.

O objetivo não é criar uma solução enterprise nem substituir ferramentas como SonarQube, Trivy ou Semgrep.

O objetivo é demonstrar conceitos de IA aplicada ao ciclo de desenvolvimento de software.

---

# Cenário da Demonstração

Um desenvolvedor abre um Pull Request.

Existem duas pipelines:

## Pipeline 1 - Genérica

Recebe:

* Git Diff

Utiliza:

* Prompt simples
* Sem tools
* Sem contexto

Resultado esperado:

* Poucos problemas encontrados
* Pouco contexto
* Baixa especialização

---

## Pipeline 2 - Estruturada

Recebe:

* Git Diff
* README.md
* catalog.yaml
* CLAUDE.md
* migration-guide.yaml

Utiliza:

* Agent SDK
* Subagentes especializados (QA, Tech Lead, Architect)
* Skills carregadas de `.claude/skills/`
* Context Engineering via `system_prompt`

Resultado esperado:

* Mais problemas encontrados
* Melhor qualidade das observações
* Entendimento do contexto do sistema

---

# Tecnologias

## Linguagem

Python

Versão:

```text
>= 3.10
```

---

## SDK

Claude Agent SDK

Instalação:

```bash
pip install claude-agent-sdk
```

---

## Modelo

Claude

Utilizar:

```text
claude-haiku-4-5-20251001
```

Configurado via `ClaudeAgentOptions`:

```python
ClaudeAgentOptions(model="claude-haiku-4-5-20251001")
```

Autenticação via variável:

```text
ANTHROPIC_API_KEY
```

---

## CLI

Utilizar Typer.

Comandos:

```bash
python -m reviewer review generic --diff examples/bad-pr.diff

python -m reviewer review structured --diff examples/bad-pr.diff
```

Opcional:

```bash
python -m reviewer review compare --diff examples/bad-pr.diff
```

---

# Estrutura do Projeto

```text
demo-ai-reviewer/

├── app-example/
│
│   ├── main.py
│   │
│   ├── handlers/
│   │   └── framework.py
│   │
│   ├── models/
│   │   └── framework.py
│   │
│   ├── docs/
│   │   └── swagger.json
│   │
│   └── tests/
│   ├── README.md
│   ├── catalog.yaml
│   ├── CLAUDE.md
│   └── migration-guide.yaml
│
├── prompts/
│
│   ├── generic.md
│   ├── structured.md
│   └── triage.md
│
├── examples/
│
│   ├── good-pr.diff
│   ├── bad-pr.diff
│   └── breaking-change.diff
│
├── tests/
│   └── prompts/
│       ├── promptfooconfig.yaml
│       ├── triage.yaml
│       └── structured.yaml
│
├── reviewer/
│
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── generic.py
│   ├── structured.py
│   ├── context.py
│   ├── reports.py
│   └── triage.py
│
├── pyproject.toml
└── requirements.txt
```

---

# Aplicação de Exemplo

Criar uma API REST simples.

Linguagem: Python com FastAPI.

Tema:

Frameworks de Prompt Engineering.

Endpoints:

```http
GET /frameworks
```

Retorna:

```json
[
  {
    "id": "rise",
    "name": "RISE"
  }
]
```

---

```http
GET /frameworks/{id}
```

Retorna:

```json
{
  "id": "rise",
  "name": "RISE",
  "description": "Role, Input, Steps, Expectation"
}
```

---

# Dados

Cadastrar alguns frameworks.

Exemplos:

* RISE
* COAST
* APE
* TAG
* CARE
* RTF

---

# Arquivos de Contexto

## catalog.yaml

Representa o catálogo do serviço.

Exemplo:

```yaml
apiVersion: backstage.io/v1alpha1

kind: Component

metadata:
  name: framework-api

spec:
  owner: platform-team
  lifecycle: production
  criticality: high
```

---

## README.md

Conter:

* Como executar
* Variáveis obrigatórias
* Endpoints
* Processo de deploy

---

## CLAUDE.md

Conter regras organizacionais.

Exemplo:

```text
Cobertura mínima 80%.

Toda variável nova deve ser documentada.

Todo endpoint novo deve atualizar o Swagger.

Breaking Changes exigem migration guide.

Não aprovar PRs com segredos hardcoded.
```

---

## migration-guide.yaml

Exemplo:

```yaml
version: 1.0

breaking_changes: []
```

---


# Prompt Genérico

Arquivo: `prompts/generic.md`

Prompt:

```text
Analise o Pull Request abaixo.

Identifique possíveis problemas.

Retorne uma lista objetiva.
```

Implementação (`reviewer/generic.py`):

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def run_generic_review(diff: str) -> str:
    prompt_template = open("prompts/generic.md").read()
    prompt = f"{prompt_template}\n\n{diff}"

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            model="claude-haiku-4-5-20251001",
            allowed_tools=[],
        ),
    ):
        if isinstance(message, ResultMessage):
            return message.result
```

---

# Triagem Pré-Execução

Antes de executar o review estruturado, executar uma chamada leve de triagem.

Objetivo: decidir se a mudança merece revisão completa ou pode ser aprovada automaticamente.

Mudanças triviais (comentários, formatação, logs) são aprovadas sem consumir tokens do review.

---

## Prompt de Triagem

Arquivo: `prompts/triage.md`

```text
Você é um triador de Pull Requests.

Analise o diff abaixo e retorne um JSON indicando se o review completo deve ser executado.

Retorne SOMENTE o JSON, sem explicações:

{
  "run": true,
  "reason": "motivo resumido"
}

Regras:
- run=true se houver: novos endpoints, lógica de negócio, variáveis de ambiente,
  remoção ou renomeação de qualquer elemento público.
- run=false se a mudança for puramente trivial: comentários, formatação, logs, typos.
```

---

## Implementação (`reviewer/triage.py`)

```python
import json
import anthropic

def run_triage(diff: str) -> bool:
    prompt_template = open("prompts/triage.md").read()

    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=128,
        messages=[
            {
                "role": "user",
                "content": f"{prompt_template}\n\n{diff}",
            }
        ],
    )

    raw = response.content[0].text.strip()
    result = json.loads(raw)
    return result.get("run", True)
```

Utiliza a API direta (`anthropic`) — não o Agent SDK — pois é uma chamada simples sem loop de agente.

---

# Prompt Estruturado

Arquivo: `prompts/structured.md`

Contém as perspectivas de revisão em seções separadas dentro do mesmo prompt.

A especialização é feita via estrutura do prompt, não via subagentes.

```text
Você é um reviewer de Pull Requests com três perspectivas:

## QA
Verifique:
- Novos endpoints ou funções possuem testes?
- Há risco de regressão?
- Casos negativos foram cobertos?

## Tech Lead
Verifique:
- O Swagger foi atualizado para novos endpoints?
- O README documenta novas variáveis de ambiente?
- O código segue as boas práticas do projeto?

## Architect
Verifique:
- Há breaking changes (endpoints removidos, variáveis renomeadas, campos alterados)?
- O migration-guide foi atualizado?
- Há impacto em outros serviços?

## Contexto do serviço
{context}

## Retorno esperado

Retorne SOMENTE o JSON:

{
  "approved": false,
  "issues": {
    "qa": [],
    "techlead": [],
    "architect": []
  }
}
```

---

## Implementação (`reviewer/structured.py`)

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from reviewer.triage import run_triage

async def run_structured_review(diff: str, context_dir: str) -> str:
    if not run_triage(diff):
        return '{"approved": true, "issues": {}, "reason": "Mudança trivial."}'

    context = load_context(context_dir)  # reviewer/context.py
    prompt = build_structured_prompt(diff, context)  # prompts/structured.md + context

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            model="claude-haiku-4-5-20251001",
            allowed_tools=[],
        ),
    ):
        if isinstance(message, ResultMessage):
            return message.result
```

---

# Pull Requests de Demonstração

Criar arquivos diff prontos.

---

## Cenário 1

Novo endpoint.

Problemas:

* Sem teste
* Sem Swagger

---

## Cenário 2

Nova variável.

```diff
+ AUTH_SECRET
```

Problemas:

* README não atualizado

---

## Cenário 3

Breaking Change.

```diff
- JWT_SECRET
+ AUTH_SECRET
```

Problemas:

* Migration guide não atualizado
* Compatibilidade quebrada

---

# Saída Esperada

## Genérico

Exemplo:

```text
Problemas encontrados:

- Possível falta de testes
- Verificar tratamento de erros
```

---

## Estruturado

Exemplo:

```json
{
  "approved": false,
  "issues": {
    "qa": ["Endpoint sem testes"],
    "techlead": ["Swagger não atualizado", "README não atualizado"],
    "architect": ["Breaking Change detectado: JWT_SECRET renomeado para AUTH_SECRET"]
  }
}
```

---

# Comparação

Implementar relatório final (`reviewer/reports.py`).

Capturar `usage` dos `AssistantMessage` durante a execução.

Exemplo:

```text
==========================
COMPARAÇÃO
==========================

Prompt Genérico

Problemas encontrados: 2

Tokens:
Input: X
Output: Y

--------------------------

Prompt Estruturado

Problemas encontrados: 9

Tokens:
Input: X
Output: Y

--------------------------

Diferença:

+350% mais problemas relevantes detectados
```

---

# Integração GitHub

Criar exemplo visual.

Não é necessário executar Action real.

Gerar arquivo markdown simulando comentário de Pull Request.

Exemplo:

```text
AI REVIEW REPORT

Status: REPROVADO

Motivos:

- Swagger desatualizado
- README desatualizado
- Breaking Change detectado
```

---

# Testes de Prompts com Promptfoo

Utilizar o [promptfoo](https://www.promptfoo.dev/) para validar o comportamento dos prompts isoladamente, sem depender da execução completa do pipeline.

## Objetivo

Garantir que cada prompt:

* Retorna JSON válido
* Detecta os problemas esperados nos cenários de teste
* Não aprova PRs com problemas conhecidos
* Não gera falsos positivos em mudanças triviais

---

## Instalação

```bash
npm install -g promptfoo
```

---

## Estrutura

Os testes ficam em `tests/prompts/`.

Arquivo raiz: `tests/prompts/promptfooconfig.yaml`

```yaml
# tests/prompts/promptfooconfig.yaml

description: "Prompt validation tests"

defaultTest:
  options:
    provider:
      id: anthropic:messages:claude-haiku-4-5-20251001

tests:
  - $ref: "./triage.yaml"
  - $ref: "./structured.yaml"
```

---

## Triage

Arquivo: `tests/prompts/triage.yaml`

```yaml
# tests/prompts/triage.yaml

- description: "Triage - run=true para novo endpoint"
  vars:
    diff: |
      diff --git a/app-example/handlers/framework.py b/app-example/handlers/framework.py
      +@app.get("/frameworks/{id}/details")
      +def get_framework_details(id: str):
      +    return {"id": id, "details": "..."}
  system: "{{file 'prompts/triage.md'}}"
  prompt: "{{diff}}"
  assert:
    - type: is-json
    - type: javascript
      value: JSON.parse(output).run === true

- description: "Triage - run=true para breaking change"
  vars:
    diff: |
      diff --git a/app-example/main.py b/app-example/main.py
      -JWT_SECRET = os.getenv("JWT_SECRET")
      +AUTH_SECRET = os.getenv("AUTH_SECRET")
  system: "{{file 'prompts/triage.md'}}"
  prompt: "{{diff}}"
  assert:
    - type: is-json
    - type: javascript
      value: JSON.parse(output).run === true

- description: "Triage - run=false para mudança trivial"
  vars:
    diff: |
      diff --git a/app-example/handlers/framework.py b/app-example/handlers/framework.py
      -    # TODO: melhorar este handler
      +    # Handler de frameworks
  system: "{{file 'prompts/triage.md'}}"
  prompt: "{{diff}}"
  assert:
    - type: is-json
    - type: javascript
      value: JSON.parse(output).run === false
```

---

## Structured

Arquivo: `tests/prompts/structured.yaml`

```yaml
# tests/prompts/structured.yaml

- description: "Structured - detecta endpoint sem teste e sem Swagger"
  vars:
    diff: |
      diff --git a/app-example/handlers/framework.py b/app-example/handlers/framework.py
      +@app.get("/frameworks/{id}/details")
      +def get_framework_details(id: str):
      +    return {"id": id, "details": "..."}
  system: "{{file 'prompts/structured.md'}}"
  prompt: "{{diff}}"
  assert:
    - type: is-json
    - type: javascript
      value: JSON.parse(output).approved === false
    - type: javascript
      value: JSON.parse(output).issues.qa.length > 0
    - type: javascript
      value: JSON.parse(output).issues.techlead.length > 0

- description: "Structured - detecta breaking change"
  vars:
    diff: |
      diff --git a/app-example/main.py b/app-example/main.py
      -JWT_SECRET = os.getenv("JWT_SECRET")
      +AUTH_SECRET = os.getenv("AUTH_SECRET")
  system: "{{file 'prompts/structured.md'}}"
  prompt: "{{diff}}"
  assert:
    - type: is-json
    - type: javascript
      value: JSON.parse(output).approved === false
    - type: javascript
      value: JSON.parse(output).issues.architect.length > 0

- description: "Structured - não reprova PR limpo"
  vars:
    diff: |
      diff --git a/app-example/tests/test_framework.py b/app-example/tests/test_framework.py
      +def test_get_framework():
      +    response = client.get("/frameworks/rise")
      +    assert response.status_code == 200
  system: "{{file 'prompts/structured.md'}}"
  prompt: "{{diff}}"
  assert:
    - type: is-json
    - type: javascript
      value: JSON.parse(output).approved === true
```

---

## Execução

```bash
# Rodar todos os testes de prompts
promptfoo eval --config tests/prompts/promptfooconfig.yaml

# Rodar prompt específico
promptfoo eval --config tests/prompts/triage.yaml

# Ver resultado no browser
promptfoo view
```

---


# Objetivo Final

Demonstrar que:

* O modelo não mudou.
* O código não mudou.
* O que mudou foi o contexto e a especialização.

Mensagem principal da palestra:

"IA não substitui conhecimento de engenharia. Ela amplifica conhecimento estruturado."
