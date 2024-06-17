FROM python:3.12-bookworm as builder
RUN pip install poetry==1.8.2
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
WORKDIR /app
COPY . .
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-dev --no-root
COPY ./src ./src
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-dev

FROM python:3.12-slim-bookworm as runtime
ENV TZ=Asia/Shanghai \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
COPY --from=builder /app /app
ENTRYPOINT ["python", "-m", "njupt_always_in_dorm"]
