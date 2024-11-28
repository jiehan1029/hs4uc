## Purpose
To easily analyze admission data and compare schools.

## Tech stack
- Python3 (poetry)
- PostgresQL, Sqlalchemy

### Install/remove dependencies
```
poetry add requests@4
```
and 
```
poetry remove requests
```

### DB migration
Generate migration file.
```
poetry run alembic revision --autogenerate -m "your-message"
```
Apply the migration.
```
poetry run alembic upgrade head
```
