#!/bin/bash

# Script de inicio simplificado para Railway
echo "🚀 === INICIANDO APLICACIÓN DJANGO ==="

echo "📊 Verificando variables de entorno..."
echo "   DEBUG: ${DEBUG:-not-set}"
echo "   MYSQL_HOST: ${MYSQL_HOST:-not-set}"
echo "   PORT: ${PORT:-8000}"

echo "🔧 === PASO 1: MIGRACIONES ==="
echo "Creando migraciones..."
python manage.py makemigrations || echo "Error en makemigrations - continuando..."

echo "Ejecutando migraciones..."
python manage.py migrate || echo "Error en migrate - continuando..."

echo "🔍 === PASO 2: VERIFICAR BASE DE DATOS ==="
python manage.py shell -c "
from core.models import Developer
try:
    count = Developer.objects.count()
    print(f'✅ Developer model OK: {count} registros')
except Exception as e:
    print(f'❌ Error Developer: {e}')
" || echo "Error en verificación - continuando..."

echo "👤 === PASO 3: SUPERUSUARIO ==="
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ Superusuario creado')
    else:
        print('✅ Superusuario existe')
except Exception as e:
    print(f'Error superusuario: {e}')
" || echo "Error en superusuario - continuando..."

echo "🚀 === PASO 4: INICIANDO SERVIDOR ==="
echo "Iniciando Gunicorn en puerto ${PORT:-8000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 portfolio.wsgi:application
