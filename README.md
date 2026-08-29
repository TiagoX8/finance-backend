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
| `LOGIN_RATE_LIMIT_ATTEMPTS` | não | `10` | Tentativas de login por janela, por IP e por e-mail. |
| `LOGIN_RATE_LIMIT_WINDOW` | não | `300` | Janela do limite de login, em segundos. |
| `REGISTER_RATE_LIMIT_ATTEMPTS` | não | `5` | Cadastros por janela, por IP. |
| `REGISTER_RATE_LIMIT_WINDOW` | não | `3600` | Janela do limite de cadastro, em segundos. |

## Segurança

- Senhas com bcrypt (salt por usuário) e mínimo de 8 caracteres; JWT HS256 com `exp`.
- Toda rota de dados exige `Authorization: Bearer` e filtra por `user_id` — não há acesso cruzado entre contas.
- `/auth/login` e `/auth/register` têm rate limiting em memória. **Ele é por processo**: com mais de uma réplica, o limite efetivo é multiplicado pelo número de réplicas. Para deploy multi-instância, trocar por um limitador com Redis.
- O rate limiting usa `X-Forwarded-For` quando presente, o que assume que a app está atrás de um proxy confiável (o caso em Render/Railway/Fly). Exposta diretamente, esse header é falsificável.
- O token é emitido para o cliente e não é revogável antes do `exp`: logout limpa o cliente, mas um token vazado continua válido até expirar. Reduza `ACCESS_TOKEN_EXPIRE_MINUTES` se isso for inaceitável.
- `/docs` fica aberto em produção; é apenas o schema, mas desabilite (`FastAPI(docs_url=None)`) se preferir não expor a superfície da API.

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
