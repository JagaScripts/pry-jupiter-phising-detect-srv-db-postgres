FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Instalar dependencias del sistema para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar el Kernel compartido (ruta corregida para coincidir con ../lib-shared-kernel desde /app)
COPY services/lib-shared-kernel /lib-shared-kernel

# Copiar archivos del proyecto
COPY services/db-postgres/pyproject.toml /app/
COPY services/db-postgres/app /app/app

ENV PYTHONPATH="/app:/lib-shared-kernel"

# Sincronizar dependencias
RUN uv sync --no-cache

# Comando por defecto para inicializar y sembrar
CMD ["uv", "run", "python", "-m", "app.seed"]
