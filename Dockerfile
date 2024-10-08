FROM python:3.10.0
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

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /mshauri

COPY poetry.lock pyproject.toml /mshauri/

# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install $(test "$ENV" == prod && echo "--no-dev") --no-interaction --no-ansi

# Creating folders, and files for project:
COPY . /mshauri

RUN chmod +x init.sh

ENTRYPOINT ["sh", "init.sh"]
