#!/bin/bash

# Script de inicio para Railway
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

echo "Creando superusuario si no existe..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

echo "Cargando datos iniciales si existen..."
if [ -f "fixtures/seed.json" ]; then
    python manage.py loaddata fixtures/seed.json
    echo "Datos iniciales cargados"
fi

echo "Iniciando servidor..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 3 portfolio.wsgi:application
