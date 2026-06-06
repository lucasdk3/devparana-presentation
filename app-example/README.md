# Framework API

API REST para listar frameworks de Prompt Engineering.

## Como executar

```bash
pip install -r requirements.txt
uvicorn app_example.main:app --reload
```

## Variáveis de ambiente

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `JWT_SECRET` | Chave secreta para autenticação JWT | Sim |
| `DATABASE_URL` | URL de conexão com o banco de dados | Não |

## Endpoints

| Método | Path | Descrição |
|--------|------|-----------|
| GET | /frameworks | Lista todos os frameworks |
| GET | /frameworks/{id} | Retorna detalhes de um framework |

## Processo de deploy

1. Criar branch a partir de `main`
2. Abrir Pull Request
3. Aguardar review automático (AI Reviewer)
4. Aprovação de pelo menos 1 engenheiro
5. Merge para `main`
6. Deploy automático via CI/CD
