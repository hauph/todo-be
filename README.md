## Migration

`alembic revision --autogenerate -m "Create tables"` - Create migration

`alembic upgrade head` - Apply migration to database

## Dev server:

`uvicorn main:app --reload --port 7000`

## Docker:

`docker compose up`

## Secret keys for SECRET_KEY and API_SECRET_KEY:

```
python3
import secrets
generated_key = secrets.token_urlsafe(30)
print(generated_key)
```