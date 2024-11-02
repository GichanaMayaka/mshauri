# First stage: Builder
FROM python:3.10.0-slim AS builder
LABEL authors="Okeyo G. Mayaka"

ARG ENV
ENV ENV=${ENV} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.3

WORKDIR /mshauri

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only dependency files first
COPY poetry.lock pyproject.toml ./

# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install $(test "$ENV" == prod && echo "--no-dev") --no-interaction --no-ansi

# Copy the rest of the application
COPY . .

# Second stage: Final
FROM python:3.10.0-slim

WORKDIR /mshauri

# Copy from builder stage
COPY --from=builder /mshauri .
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

RUN chmod +x init.sh

ENTRYPOINT ["sh", "init.sh"]
