# =============================================================================
# Stage 1: Dependencies - Cached layer for requirements
# =============================================================================
FROM python:3.11-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-connector-c-dev \
    pkgconfig

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install gunicorn -r requirements.txt


# =============================================================================
# Stage 2: Testing (optional) - Run tests before production
# =============================================================================
FROM python:3.11-alpine AS testing

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache mariadb-connector-c

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Install test dependencies (makes this stage larger)
RUN pip install --no-cache-dir pytest pytest-cov coverage

COPY . .
# RUN pytest tests/


# =============================================================================
# Stage 3: Production - Final minimal image
# =============================================================================
FROM python:3.11-alpine AS production

WORKDIR /app

# Only runtime dependencies - no gcc, no pytest
RUN apk add --no-cache mariadb-connector-c \
    && adduser -D -h /app appuser

# Copy only production packages (no test tools)
COPY --from=builder /install /usr/local

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

RUN mkdir -p templates

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]
