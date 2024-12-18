### What is it??
This project is done during the Thanksgiving holiday when I started to study local high schools for the kid. As the name suggests, HS4UC (high school for UC), I'm trying to compare the local school's admission rate to certain UC campuses in recent years. Nature of the project is therefore very personal, aiming to have something done fast, and analysis may not be that accurate, and I don't plan to expand it (holiday is ending). There is also an frontend app for its visualization (HS4UC-vis).


### Data source
This project only focus on high schools in California and admission data of UC campuses. I used the following data.

High school graduate stats by school: https://www.cde.ca.gov/ta/ac/cm/graddatafiles.asp

UC Admission stats: https://www.universityofcalifornia.edu/about-us/information-center/admissions-source-school



### Tech stack
Python3, FastAPI, PostgresQL, Sqlalchemy, Alembic


### Run in localhost
Assume relevant spreadsheets are ready (see `import_data.py`).

First spin up container with `docker compose build` and `docker compose up`.

Second install dependencies locally (since I saved the spreadsheets in desktop) `poetry install` and then run migration `poetry run alembic upgrade head`. After that, import data by running the methods inside `import_data.py` from poetry env's python shell (`poetry run python`).

Now everything is ready. Check out localhost:8000/analyze.

