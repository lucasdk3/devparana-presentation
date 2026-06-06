# Regras Organizacionais - Framework API

## Testes

Cobertura mínima: 80%.

Todo endpoint novo deve ter testes unitários e de integração.

Casos negativos devem ser cobertos.

## Documentação

Toda variável de ambiente nova deve ser documentada no README.md.

Todo endpoint novo deve atualizar o Swagger em `docs/swagger.json`.

## Breaking Changes

Breaking Changes exigem migration guide atualizado em `migration-guide.yaml`.

Não renomear variáveis de ambiente sem adicionar período de compatibilidade.

## Segurança

Não aprovar PRs com segredos hardcoded.

Não logar valores de variáveis de ambiente sensíveis.

## Qualidade

Não usar `print()` em código de produção — usar o logger configurado.

Funções com mais de 30 linhas devem ser refatoradas.
