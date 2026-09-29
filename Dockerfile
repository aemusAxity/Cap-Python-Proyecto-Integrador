FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.0.0


RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./
COPY README.md ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

RUN poetry build

FROM python:3.12-slim AS runner

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


COPY --chown=appuser:appgroup --from=builder /build/dist/*.whl ./
COPY --chown=appuser:appgroup --from=builder /build/alembic ./alembic
COPY --chown=appuser:appgroup --from=builder /build/alembic.ini ./alembic.ini

RUN pip install --no-cache-dir ./*.whl
RUN pip install --no-cache-dir alembic

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
