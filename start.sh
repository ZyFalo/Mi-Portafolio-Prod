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
usuario = User.objects.filter(username=username).first()
if usuario is None:
    User.objects.create_superuser(username=username, email=email, password=password)
    print('[start] Superuser created')
else:
    # Vía de recuperación: si se pierde el acceso, basta con cambiar la
    # variable en Railway y volver a desplegar. Evita tener que dejar
    # credenciales escritas en el repositorio.
    usuario.set_password(password)
    usuario.email = email
    usuario.is_staff = True
    usuario.is_superuser = True
    usuario.save()
    print('[start] Superuser password updated from environment')
PY
fi

echo "[start] Launching Gunicorn on ${PORT:-8000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 portfolio.wsgi:application
