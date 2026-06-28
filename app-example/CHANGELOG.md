# Changelog

Todas as modificações desse projeto devem ser adicionadas a esse arquivo.

O formato foi baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e o projeto está seguindo o versionamento conforme [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-06-28

### Added
- Endpoint `GET /frameworks` — lista todos os frameworks de Prompt Engineering disponíveis
- Endpoint `GET /frameworks/{id}` — retorna detalhes de um framework específico por ID (404 se não encontrado)
- Modelos disponíveis: `RISE`, `COAST`, `APE`, `TAG`, `CARE`, `RTF`
- Variável de ambiente `JWT_SECRET` obrigatória para autenticação
- Swagger documentando os dois endpoints em `docs/swagger.json`

## [0.1.0] - 2026-05-15

### Added
- Setup inicial do projeto com FastAPI
- Estrutura base: `handlers/`, `models/`, `tests/`
- Modelo `Framework` com campos `id`, `name` e `description`
