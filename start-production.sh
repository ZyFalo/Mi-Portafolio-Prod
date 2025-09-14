#!/bin/bash

# Script de inicio para producción en Railway
echo "🚀 Iniciando aplicación Django..."

# Ejecutar migraciones
echo "📦 Aplicando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Crear superusuario si no existe
echo "👤 Configurando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superusuario creado')
else:
    print('✅ Superusuario ya existe')
"

# Verificar que los modelos principales funcionan
echo "🔍 Verificando base de datos..."
python manage.py shell -c "
from core.models import Developer
print(f'✅ Base de datos OK - {Developer.objects.count()} desarrolladores')
"

echo "🌐 Iniciando servidor en puerto ${PORT:-8000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 portfolio.wsgi:application
