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

# Copy ONLY requirements first (better cache utilization)
COPY requirements.txt .

# Install to separate directory for clean copy
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt gunicorn

# =============================================================================
# Stage 2: Testing - For CI/CD test stage
# =============================================================================
FROM python:3.11-alpine AS testing

WORKDIR /app

# Install runtime + netcat for DB checks
RUN apk add --no-cache mariadb-connector-c

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Install test dependencies
RUN pip install --no-cache-dir pytest pytest-cov

# Copy application code
COPY . .

# Default command for testing
CMD ["pytest", "tests/", "-v", "--tb=short"]

# =============================================================================
# Stage 3: Production - Final minimal image
# =============================================================================
FROM python:3.11-alpine AS production

WORKDIR /app

# Install runtime dependencies + netcat for healthchecks
RUN apk add --no-cache \
    mariadb-connector-c \
    curl \
    && adduser -D -h /app appuser

# Copy only production packages
COPY --from=builder /install /usr/local

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

# Copy application code
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 5000

# Healthcheck built into image
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/auth/check || exit 1

CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:create_app()"]
