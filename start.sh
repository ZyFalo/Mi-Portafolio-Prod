#!/bin/bash

# Script de inicio para Railway con mejor logging
set -e  # Salir si cualquier comando falla

echo "🚀 Iniciando aplicación Django en Railway..."
echo "📊 Variables de entorno:"
echo "   - DEBUG: ${DEBUG:-not-set}"
echo "   - RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-not-set}"
echo "   - MYSQL_HOST: ${MYSQL_HOST:-not-set}"
echo "   - ALLOWED_HOSTS: ${ALLOWED_HOSTS:-not-set}"

echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput

echo "👤 Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superusuario creado: admin/admin123')
else:
    print('✅ Superusuario ya existe')
"

echo "📦 Cargando datos iniciales..."
if [ -f "fixtures/seed.json" ]; then
    python manage.py loaddata fixtures/seed.json
    echo "✅ Datos iniciales cargados"
else
    echo "ℹ️  No se encontraron fixtures para cargar"
fi

echo "🌐 Verificando configuración Django..."
python manage.py check --deploy

echo "🚀 Iniciando servidor Gunicorn en puerto ${PORT:-8000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 --access-logfile - --error-logfile - portfolio.wsgi:application
