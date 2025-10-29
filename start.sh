#!/bin/bash
set -euo pipefail

echo "[start] Applying migrations..."
python manage.py migrate --noinput

# Create additional superuser: zyfalo
echo "[start] Creating additional superuser 'zyfalo'..."
python - <<'PY'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings.production')
django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()
username = 'zyfalo'
email = 'zyfalo@admin.com'
password = 'admin123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('[start] Additional superuser "zyfalo" created successfully')
else:
    print('[start] Additional superuser "zyfalo" already exists')
PY

# Optional superuser creation via env vars
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
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('[start] Superuser created')
else:
    print('[start] Superuser already exists')
PY
fi

echo "[start] Launching Gunicorn on ${PORT:-8000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 portfolio.wsgi:application
