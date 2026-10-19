# Official lightweight Python base image
FROM python:3.10-slim

# Set environment variables for Python performance and Docker container safety
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install runtime dependencies (curl for container health checks)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root system user and group for security
RUN groupadd -g 1000 appgroup \
    && useradd -u 1000 -g appgroup -m -s /bin/bash appuser

# Set working directory and assign ownership
WORKDIR /app
RUN chown appuser:appgroup /app

# Copy dependency requirements first to leverage Docker layer caching
COPY --chown=appuser:appgroup requirements.txt .

# Install dependencies into system Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and configuration with ownership assigned to appuser
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Expose FastAPI default application port
EXPOSE 8000

# Production startup command (reload disabled for production stability)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

