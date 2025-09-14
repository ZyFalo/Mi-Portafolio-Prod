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

# Recopilar archivos estáticos y preparar migraciones
RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations

# Crear script que se ejecute automáticamente en runtime
RUN echo '#!/bin/bash\npython manage.py migrate\npython manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(\"admin\", \"admin@example.com\", \"admin123\") if not User.objects.filter(username=\"admin\").exists() else print(\"Admin exists\")"' > /app/init-db.sh
RUN chmod +x /app/init-db.sh

# Crear un usuario no-root para ejecutar la aplicación
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Exponer el puerto
EXPOSE $PORT

# Comando para ejecutar la aplicación
ENTRYPOINT ["./start.sh"]
