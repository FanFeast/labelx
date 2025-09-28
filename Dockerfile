# Multi-stage Dockerfile (bootstrap)

FROM python:3.11-slim AS base
WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src
RUN pip install --no-cache-dir .

FROM base AS runtime
ENTRYPOINT ["annox"]
CMD ["--help"]

