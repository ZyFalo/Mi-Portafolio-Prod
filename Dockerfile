# Imagen base optimizada para producción
FROM python:3.12-slim

# Variables de entorno para producción
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para MySQL
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       default-libmysqlclient-dev \
       pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias Python
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copiar código de la aplicación (start.sh ya viene como 100755 desde git)
COPY . .

# Entrypoint explícito con permisos en build (evita cualquier `RUN chmod`,
# que falla con "Operation not permitted" en builders rootless como Railway)
COPY --chmod=755 docker/entrypoint.sh /entrypoint.sh

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput

# Crear usuario no-root para seguridad y dar permisos
RUN useradd -m appuser \
    && chown -R appuser:appuser /app

# Cambiar al usuario no-root
USER appuser

# Exponer puerto
EXPOSE $PORT

# Comando de inicio
CMD ["/entrypoint.sh"]
