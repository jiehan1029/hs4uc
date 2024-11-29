## Purpose
To easily analyze admission data and compare schools.

## Data source
This project only focus on high schools in Santa Clara County.

High school graduate stats by school: https://www.cde.ca.gov/ta/ac/cm/graddatafiles.asp

UC Admission stats: https://www.universityofcalifornia.edu/about-us/information-center/admissions-source-school

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
