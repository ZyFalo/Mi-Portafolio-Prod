#!/bin/bash
set -euo pipefail

echo "[start] Applying migrations..."
python manage.py migrate --noinput

# El superusuario se crea solo a partir de variables de entorno.
# Antes se creaba uno con credenciales escritas en este mismo archivo, que
# vive en un repositorio publico: cualquiera podia leerlas.

# Creacion del superusuario mediante variables de entorno
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "[start] Ensuring superuser exists (${DJANGO_SUPERUSER_USERNAME})..."
  python - <<'PY'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings.production')
import django
django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ['DJANGO_SUPERUSER_USERNAME']
email = os.environ['DJANGO_SUPERUSER_EMAIL']
password = os.environ['DJANGO_SUPERUSER_PASSWORD']
# Solo se crea la cuenta si no existe. Nunca se reescribe la contraseña de
# una cuenta ya creada: si se hiciera, cada despliegue revertiría el cambio
# que se hubiera hecho desde el propio panel de administración.
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('[start] Superuser created')
else:
    print('[start] Superuser already exists, left untouched')
PY
fi

echo "[start] Launching Gunicorn on ${PORT:-8000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 portfolio.wsgi:application
