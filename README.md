# Finance SaaS Backend

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

## Variáveis de ambiente

Veja `.env.example`:

| Variável | Obrigatória | Padrão | Descrição |
| --- | --- | --- | --- |
| `DATABASE_URL` | sim | — | String de conexão do Postgres. |
| `SECRET_KEY` | sim | — | Chave de assinatura dos JWTs. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | não | `1440` | Expiração do token de acesso. |
| `ALLOWED_ORIGINS` | não | `http://localhost:5173` | Origens liberadas no CORS, separadas por vírgula. |

## Migrations (Alembic)

```bash
# aplicar todas as migrations
alembic upgrade head

# criar uma nova migration a partir das mudanças em app/models.py
alembic revision --autogenerate -m "descricao"

# voltar uma migration
alembic downgrade -1
```

O Alembic lê a conexão de `DATABASE_URL` (`alembic/env.py`), então `alembic.ini` não guarda credenciais.
