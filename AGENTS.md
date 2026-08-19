# AGENTS.md — Guía operativa del proyecto

Este archivo es una guía rápida para agentes/colaboradores que necesitan entender, ejecutar y modificar este proyecto sin romper comportamiento clave.

## Resumen rápido

- Proyecto: portafolio en Django con apps para home, contacto, FAQ, gadgets y analítica.
- Framework: Django 5.0.7.
- DB: SQLite (local) o MySQL (prod).
- Frontend: Bootstrap 5.3 + JS propio.
- Tracking: GTM/GA4 con dataLayer.

## Estructura del repo (rutas clave)

- `portfolio/` código del proyecto y apps.
- `portfolio/apps/core/` home y red de desarrolladores.
- `portfolio/apps/contact/` formulario de contacto, anti‑bot y reCAPTCHA.
- `portfolio/apps/faq/` preguntas frecuentes.
- `portfolio/apps/openapp/` gadgets/setups.
- `portfolio/apps/analytics/` context processor de tracking.
- `portfolio/settings/` settings base/local/production.
- `templates/` templates por app + `base.html`.
- `static/` CSS/JS fuente.
- `staticfiles/` salida de `collectstatic` (no editar).
- `fixtures/seed.json` datos de ejemplo.
- `docs/analytics/README.md` guía de eventos GA4/GTM.
- `start.sh` entrypoint de producción.
- `Dockerfile` imagen de producción.

## Stack y versiones

- Python: README sugiere 3.13, Docker usa 3.12‑slim.
- Django 5.0.7.
- WhiteNoise 6.7.0.
- Gunicorn 22.0.0.
- mysqlclient 2.2.4.
- dj-database-url 2.1.0.

## Configuración rápida (local)

1) Crear y activar venv:

```bash
python -m venv .venv
. .venv/bin/activate
```

2) Instalar dependencias:

```bash
pip install -r requirements-dev.txt
```

3) Migraciones + datos (opcional):

```bash
python manage.py migrate
python manage.py loaddata fixtures/seed.json
```

4) Ejecutar:

```bash
python manage.py runserver
```

## Variables de entorno (principales)

Revisar `.env.example`. Claves principales:

- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.
- `DATABASE_URL` o `MYSQL_*`.
- `GTM_CONTAINER_ID`, `GA_MEASUREMENT_ID`.
- `RECAPTCHA_SITE_KEY`, `RECAPTCHA_SECRET_KEY`, `RECAPTCHA_ENABLED`.
- `PORT` (Gunicorn).
- `DJANGO_SUPERUSER_*` (crear superusuario en producción).

## Apps y responsabilidades

- `core`: muestra home con `Developer`.
  - Modelo: `portfolio/apps/core/models.py`.
  - Vistas: `portfolio/apps/core/views.py`.
- `contact`: formulario + anti‑bot + reCAPTCHA.
  - Model: `ContactMessage` en `portfolio/apps/contact/models.py`.
  - Validación: `portfolio/apps/contact/forms.py`.
  - Lógica reCAPTCHA: `portfolio/apps/contact/views.py`.
- `faq`: preguntas frecuentes (`Question`).
  - `portfolio/apps/faq/models.py`.
- `openapp`: gadgets/setups (`OpenEntity`, `Tag`).
  - `portfolio/apps/openapp/models.py`.
- `analytics`: inyección de IDs de tracking.
  - `portfolio/apps/analytics/context_processors.py`.

## URLs principales

Definidas en `portfolio/urls.py`:

- `/` home.
- `/contactame/` contacto.
- `/fyq/` FAQ.
- `/open/` gadgets y detalles.
- `/admin/` Django Admin.

## Frontend

- Base: `templates/base.html` (layout + GTM/GA4).
- Templates por app en `templates/core/`, `templates/contact/`, `templates/faq/`, `templates/openapp/`.
- JS principal: `static/js/portfolio.js`.
- CSS principal: `static/css/portfolio.css`.

## Analítica y tracking

Eventos y guía completa en `docs/analytics/README.md`.

Notas:
- Se usa `dataLayer` en `templates/base.html`.
- GA4 fallback con `gtag` si no hay GTM.
- No duplicar `page_view`: o lo maneja GTM automático o el custom event.

## Despliegue (Docker/Railway)

`Dockerfile`:
- Instala deps del sistema para MySQL.
- Corre `collectstatic`.
- Ejecuta `/entrypoint.sh` (que delega a `start.sh`).

`start.sh`:
- Migra BD.
- Crea un superusuario solo si están definidas las variables `DJANGO_SUPERUSER_*`.
- Opcional: crea superusuario desde env vars `DJANGO_SUPERUSER_*`.

`docker/entrypoint.sh`:
- Script mínimo que ejecuta `/app/start.sh`.

Notas para Railway (errores conocidos):
- Si el log muestra `chmod +x /entrypoint.sh` con `Operation not permitted`, se evita usando `COPY --chmod=755 docker/entrypoint.sh /entrypoint.sh` (BuildKit) y eliminando el `chmod`.
- Verifica que Railway esté construyendo el último commit y el Dockerfile actual del repo.
- `chmod` debe ocurrir antes de `USER appuser` para tener permisos.

## Guardrails (evitar romper)

- No editar `staticfiles/` directo.
- Mantener los eventos GA4 y el `dataLayer` en `templates/base.html`.
- No remover el anti‑bot del formulario (`website`, `ts`) ni la validación reCAPTCHA si está activada.
- Si se cambia el layout, validar que los IDs/anchors usados por JS sigan existiendo.
- Evitar duplicar `page_view` en GTM/GA4.

## Riesgos/contras conocidos

- Desalineación de versión de Python (README 3.13 vs Docker 3.12).
- `start.sh` crea un superusuario fijo con credenciales conocidas: revisar antes de producción.

## Comandos útiles

- Validaciones Django:
  - `python manage.py check`
  - `python manage.py test`

## Si vas a modificar algo

- Cambios de modelos: correr migraciones.
- Cambios en estáticos: volver a correr `collectstatic` para prod.
- Cambios en analytics: actualizar `docs/analytics/README.md` con eventos nuevos.
