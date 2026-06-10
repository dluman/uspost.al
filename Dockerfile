# syntax=docker/dockerfile:1

# ───────────────────────────────────────────────────────────
# Stage 1: Build dependencies
# ───────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

# Copy dependency files for installation
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# ───────────────────────────────────────────────────────────
# Stage 2: Production image
# ───────────────────────────────────────────────────────────
FROM python:3.14-slim-bookworm AS production

# Create a non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appgroup uspost_al/ ./uspost_al/
COPY --chown=appuser:appgroup main.py ./

# Ensure the virtual environment is in the path
ENV PATH="/app/.venv/bin:$PATH"

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application with Uvicorn
# Use exec form for proper signal handling
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# ───────────────────────────────────────────────────────────
# Stage 3: Development image (optional, includes all files)
# ───────────────────────────────────────────────────────────
FROM production AS development

USER root

# Copy remaining project files for development
COPY --chown=appuser:appgroup pyproject.toml uv.lock ./

USER appuser

# Enable auto-reload for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
