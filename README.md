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

## Deploy

A imagem roda `alembic upgrade head` antes de subir o servidor (`entrypoint.sh`), então o schema é aplicado a cada release.

```bash
docker build -t finance-backend .
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:senha@host:5432/finance \
  -e SECRET_KEY=... \
  -e ALLOWED_ORIGINS=https://seu-frontend.com \
  finance-backend
```

O servidor escuta em `$PORT` (padrão `8000`), o que atende provedores que injetam a porta (Render, Railway, Fly, Cloud Run). Para plataformas baseadas em buildpack existe também um `Procfile`, com as migrations na fase de `release`.

Checklist do provedor:

1. Provisionar um Postgres e usar a connection string dele em `DATABASE_URL` (`postgres://` também é aceito e normalizado).
2. Definir `SECRET_KEY` como secret, com valor aleatório: `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Trocar essa chave invalida todos os tokens emitidos.
3. Definir `ALLOWED_ORIGINS` com o domínio exato do frontend (sem barra final); múltiplos domínios separados por vírgula.
4. Apontar o healthcheck para `GET /health`.

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
