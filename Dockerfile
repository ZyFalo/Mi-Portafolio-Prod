# Usar Python 3.13 como imagen base
FROM python:3.13-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Instalar dependencias del sistema necesarias para MySQL
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Dar permisos de ejecución al script de inicio
RUN chmod +x start.sh

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput

# Crear un usuario no-root para ejecutar la aplicación
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Exponer el puerto
EXPOSE $PORT

# Comando para ejecutar la aplicación
CMD ["./start.sh"]
