## Migration

`alembic revision --autogenerate -m "Create tables"` - Create migration

`alembic upgrade head` - Apply migration to database

## Dev server:

`uvicorn main:app --reload --port 7000`

## Docker:

`docker compose up`

