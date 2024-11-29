
FROM python:3.13

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock

# install poetry
RUN pip install poetry

RUN poetry install

COPY ./app /code/app

# CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "--port", "8000", "app/main.py", "--reload"]