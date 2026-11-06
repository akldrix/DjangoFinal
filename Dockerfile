FROM python:3.15-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip "poetry==2.5.1"
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY mysite .
RUN [ "python", "manage.py", "collectstatic", "--noinput"]
CMD ['gunicorn', 'mysite.wsgi:application', '--bind', '0.0.0.0:8000']
