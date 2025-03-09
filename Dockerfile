FROM python:3.11-slim as builder

ARG POETRY_VERSION=1.8.3
ARG POETRY_WITH=false

ENV POETRY_HOME=/opt/poetry

ENV POETRY_HOME=/opt/poetry
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_VIRTUALENVS_CREATE=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_CACHE_DIR=/opt/.cache

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN if [ $POETRY_WITH = "false" ]; then \
      poetry install --sync --without dev,local --no-root;  \
    else \
      poetry install --sync --without dev,local --with "$POETRY_WITH" --no-root; \
    fi

COPY src ./src
RUN if [ $POETRY_WITH = "false" ]; then \
      poetry install --sync --without dev --no-root && rm -rf $POETRY_CACHE_DIR;  \
    else \
      poetry install --sync --without dev --with "$POETRY_WITH" --no-root && rm -rf $POETRY_CACHE_DIR; \
    fi


FROM python:3.11-slim as runtime

EXPOSE 8000

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app
COPY ./src ./src

FROM runtime as test

COPY pyproject.toml .
COPY ./tests ./tests

CMD ["pytest"]

FROM runtime as dbinit

CMD ["python3", "-m", "connectai", "start", "dbinit"]

FROM runtime as eval

CMD ["sh", "-c", "python -m connectai.evaluation.state_classification.evaluator && python -m connectai.evaluation.conversation_output_agent.evaluator"]

FROM runtime as backend

CMD ["python3", "-m", "connectai", "start", "backend"]
