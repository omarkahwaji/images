# syntax=docker/dockerfile:1
FROM python:3.11-slim-bullseye

WORKDIR /app

COPY pyproject.toml ./
COPY poetry.lock ./

# Install the necessary libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

COPY . .

CMD python wait_for_db.py && uvicorn main:app --host 0.0.0.0 --port 8080
