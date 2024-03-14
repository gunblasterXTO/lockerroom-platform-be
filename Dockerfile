# syntax=docker/dockerfile:1

###############################
# Base Image
###############################
ARG PYTHON_VERSION=3.12.1-slim
FROM python:${PYTHON_VERSION} as python-base

ENV \
    # Prevents Python from writing pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # Keeps Python from buffering stdout and stderr to avoid situations where
    # the application crashes without emitting any logs due to buffering
    PYTHONUNBUFFERED=1 \
    # Disable a pip version check to reduce run-time
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Cache is useless in Docker Image
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1 \
    # Poetry without user interaction
    POETRY_NO_INTERACTION=1 \
    # Not necessary to create virtual environment in Docker (add overhead)
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    # Application path
    PYSETUP_PATH="/app"

###############################
# Builder Image
###############################
FROM python-base as build

# Copy project dependencies
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# Install poetry and dependencies
RUN pip install poetry==$POETRY_VERSION \
    && poetry install --no-dev --no-root --no-ansi \
    && poetry export -f requirements.txt -o requirements.txt

###############################
# Final Image
###############################
FROM python-base as final

WORKDIR $PYSETUP_PATH

COPY --from=build $PYSETUP_PATH/requirements.txt ./

RUN \
    # Upgrade package index and install security update
    apt-get update \
    && apt-get upgrade -y \
    # Install dependencies
    && pip install -r requirements.txt \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y

COPY ./main.py ./sqlite.db ./
COPY ./app app

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD uvicorn main:app --host 0.0.0.0 --port 8000
