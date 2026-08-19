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
# Se comprueba si ya hay ALGÚN superusuario, no solo el de este nombre: así
# un cambio de DJANGO_SUPERUSER_USERNAME no acaba creando una segunda cuenta
# con acceso total. Si ya existe alguna, no se toca nada — ni contraseñas ni
# permisos —, de modo que lo que se cambie desde el panel sobrevive a los
# despliegues.
if User.objects.filter(is_superuser=True).exists():
    print('[start] A superuser already exists, nothing to do')
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print('[start] No superuser found: initial account created')
PY
fi

echo "[start] Launching Gunicorn on ${PORT:-8000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 portfolio.wsgi:application
