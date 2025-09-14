#!/bin/bash

# Script de inicio para Railway con debugging y manejo de errores robusto
set -e  # Salir si cualquier comando falla

echo "🚀 Iniciando aplicación Django en Railway..."
echo "📊 Variables de entorno Railway:"
echo "   - RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-not-set}"
echo "   - RAILWAY_PROJECT_ID: ${RAILWAY_PROJECT_ID:-not-set}"
echo "   - RAILWAY_SERVICE_ID: ${RAILWAY_SERVICE_ID:-not-set}"
echo "   - DATABASE_URL: ${DATABASE_URL:+set}${DATABASE_URL:-not-set}"

echo "🗄️ Variables MySQL:"
echo "   - MYSQL_HOST: ${MYSQL_HOST:-not-set}"
echo "   - MYSQLHOST: ${MYSQLHOST:-not-set}"
echo "   - MYSQL_DATABASE: ${MYSQL_DATABASE:-not-set}"
echo "   - MYSQLDATABASE: ${MYSQLDATABASE:-not-set}"
echo "   - MYSQL_USER: ${MYSQL_USER:-not-set}"
echo "   - MYSQLUSER: ${MYSQLUSER:-not-set}"
echo "   - MYSQL_PORT: ${MYSQL_PORT:-not-set}"
echo "   - MYSQLPORT: ${MYSQLPORT:-not-set}"

echo "⚙️ Variables de aplicación:"
echo "   - DEBUG: ${DEBUG:-not-set}"
echo "   - ALLOWED_HOSTS: ${ALLOWED_HOSTS:-not-set}"
echo "   - SECRET_KEY: ${SECRET_KEY:+set}${SECRET_KEY:-not-set}"
echo "   - PORT: ${PORT:-8000}"

echo "🔍 Verificando conectividad MySQL..."
if [ ! -z "${MYSQL_HOST}" ] || [ ! -z "${MYSQLHOST}" ]; then
    echo "✅ Variables MySQL detectadas"
else
    echo "⚠️ No se detectaron variables MySQL - usando SQLite como fallback"
fi

echo "� Creando migraciones si es necesario..."
python manage.py makemigrations --dry-run --verbosity=2
python manage.py makemigrations

echo "🔄 Ejecutando migraciones con verbose..."
python manage.py migrate --verbosity=2

echo "🔍 Verificando estado de la base de datos..."
python manage.py shell -c "
import django
from django.db import connection
from django.apps import apps

# Verificar todas las tablas instaladas
print('📋 Tablas disponibles:')
with connection.cursor() as cursor:
    if 'sqlite' in connection.vendor:
        cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table';\")
    else:
        cursor.execute('SHOW TABLES;')
    
    tables = cursor.fetchall()
    for table in tables:
        print(f'   - {table[0]}')

# Verificar específicamente core_developer
try:
    from core.models import Developer
    count = Developer.objects.count()
    print(f'✅ Modelo Developer accesible: {count} registros')
except Exception as e:
    print(f'❌ Error con modelo Developer: {e}')

print('🎯 Verificación completada')
"

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
python manage.py check

echo "🚀 Iniciando servidor Gunicorn en puerto ${PORT:-8000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 --access-logfile - --error-logfile - portfolio.wsgi:application
