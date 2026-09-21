# Stage 1: Build virtual environment with uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Enable bytecode compilation and copy mode for uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy project definition and lockfile for optimal layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies without installing the project itself yet
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy application source
COPY src/ ./src/
COPY README.md ./

# Sync to install the application package
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Stage 2: Runtime image
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# Set runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PORT=8000 \
    ENVIRONMENT="production" \
    DEBUG=false

# Create non-root user for security compliance
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh appuser

# Copy virtual environment and source code
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/src /app/src
COPY --from=builder --chown=appuser:appgroup /app/pyproject.toml /app/pyproject.toml

# Switch to non-root user
USER appuser

# Expose backend port
EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

# Launch ASGI server
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
