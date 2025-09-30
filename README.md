# Portafolio Django — Gadgets & Setups

Sitio de portafolio profesional construido con Django 5 que combina CV, red de desarrolladores, galería de gadgets y formulario de contacto avanzado. Todo se administra desde Django Admin y está instrumentado con eventos para Google Tag Manager (GTM) y Google Analytics 4 (GA4).

## Tabla de contenidos

- [Características principales](#caracter%C3%ADsticas-principales)
- [Stack y dependencias](#stack-y-dependencias)
- [Arquitectura rápida](#arquitectura-r%C3%A1pida)
- [Entorno local](#entorno-local)
- [Datos de ejemplo](#datos-de-ejemplo)
- [Variables de entorno](#variables-de-entorno)
- [Analítica y tracking](#anal%C3%ADtica-y-tracking)
- [Frontend y experiencia de usuario](#frontend-y-experiencia-de-usuario)
- [Pruebas y verificación](#pruebas-y-verificaci%C3%B3n)
- [Despliegue en Railway (Docker)](#despliegue-en-railway-docker)
- [Documentación adicional](#documentaci%C3%B3n-adicional)

## Características principales

- **Home** con CV completo, badges de habilidades y red de desarrolladores que generan URLs con UTM automáticas para atribución.
- **Formulario de contacto** con validación en vivo, honeypot, timestamp anti-bot y soporte opcional para Google reCAPTCHA v2. Cada envío queda guardado en `ContactMessage`.
- **FAQ** administrables con acordeón accesible y orden configurable desde el CMS.
- **Gadgets & Setups (OpenApp)** con grid responsive, detalle por slug, tags (`Tag`) y eventos GA4 para vistas y clics.
- **Panel Django Admin** como CMS central: crea/ordena desarrolladores, preguntas, gadgets y mensajes.
- **Tracking completo**: dataLayer inicializado, eventos custom + GA4 estándar, fallback automático a `gtag` si no hay contenedor GTM.
- **Preparado para producción** con WhiteNoise, Dockerfile optimizado, script `start.sh` y soporte MySQL/SQLite.

## Stack y dependencias

- Python 3.13
- Django 5.0.7
- SQLite (desarrollo) / MySQL (producción)
- Bootstrap 5.3 + Bootstrap Icons vía CDN
- WhiteNoise para servir estáticos en producción
- Gunicorn (contenedores)

Revisa `requirements-base.txt`, `requirements-dev.txt` y `requirements.txt` para ver dependencias por entorno.

## Arquitectura rápida

```
portfolio/
├─ apps/
│  ├─ core (home + red de desarrolladores)
│  ├─ contact (formulario público + anti-bot + reCAPTCHA)
│  ├─ faq (preguntas frecuentes administrables)
│  ├─ openapp (gadgets, tags, vistas pública)
│  └─ analytics (context processor con IDs de seguimiento)
├─ settings/ (base, local, production)
└─ urls.py, wsgi.py, asgi.py

templates/
├─ base.html (layout + GTM/GA4 + payload UTM)
├─ core/, contact/, faq/, openapp/
static/
├─ css/portfolio.css
└─ js/portfolio.js (UI + dataLayer events)
```

## Entorno local

1. Instala Python 3.13 y crea un entorno virtual:

   ```bash
   python -m venv .venv
   . .venv/Scripts/activate  # PowerShell: .\.venv\Scripts\Activate.ps1
   ```

2. Instala dependencias de desarrollo (sin `mysqlclient`):

   ```bash
   pip install -r requirements-dev.txt
   ```

3. Ejecuta migraciones y (opcional) carga datos de ejemplo:

   ```bash
   python manage.py migrate
   python manage.py loaddata fixtures/seed.json
   ```

4. Crea un superusuario y levanta el servidor local:

   ```bash
   python manage.py createsuperuser
   python manage.py runserver
   ```

La configuración local usa `portfolio.settings.local` por defecto. Visita `http://127.0.0.1:8000` y `/admin/`.

## Datos de ejemplo

El fixture `fixtures/seed.json` agrega:

- 3 preguntas frecuentes activas.
- 6 gadgets con tags asociados.
- Datos iniciales para probar las vistas públicas.

Cárgalo con `python manage.py loaddata fixtures/seed.json` y borra/modifica los registros desde el admin según tus necesidades.

## Variables de entorno

| Variable | Descripción |
| --- | --- |
| `SECRET_KEY` | Clave secreta de Django (obligatoria en producción). |
| `DEBUG` | `1`/`0`. En local es `1` por defecto. |
| `ALLOWED_HOSTS` | Lista separada por comas. Por defecto `localhost,127.0.0.1` si `DEBUG=1`. |
| `CSRF_TRUSTED_ORIGINS` | Orígenes completos (https://dominio) separados por coma. |
| `DATABASE_URL` | Cadena compatible con `dj-database-url` (prioritaria). |
| `MYSQL_HOST`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_PORT` | Alternativa si no usas `DATABASE_URL`. |
| `GTM_CONTAINER_ID` | ID de contenedor GTM (GTM-XXXXXX). |
| `GA_MEASUREMENT_ID` | Medición GA4 utilizada como fallback cuando no hay GTM. |
| `RECAPTCHA_SITE_KEY` | Clave pública v2 (opcional). |
| `RECAPTCHA_SECRET_KEY` | Clave privada v2 (opcional). |
| `RECAPTCHA_ENABLED` | `1`/`0`. Controla si se exige reCAPTCHA (por defecto `1`). |
| `DJANGO_SETTINGS_MODULE` | `portfolio.settings.production` en producción (`manage.py` ya configura `local`). |
| `PORT` | Puerto para Gunicorn en contenedor (por defecto 8000). |
| `DJANGO_SUPERUSER_*` | `USERNAME`, `EMAIL`, `PASSWORD` para autocrear superusuario desde `start.sh`. |

## Analítica y tracking

- `portfolio.apps.analytics.context_processors.analytics` inyecta `GTM_CONTAINER_ID`, `GA_MEASUREMENT_ID`, `RECAPTCHA_SITE_KEY` y flags al template base.
- `base.html` inicializa `dataLayer`, envía `page_view` con UTMs y carga GTM/GA4 según disponibilidad.
- Eventos destacados:
  - `developer_portfolio_click`, `banner_click`, `developer_card_click`, `section_view` en la home.
  - `contact_form_submit`, `contact_submit_success`, `generate_lead` en el formulario.
  - `view_item_list`, `select_content`, `gadget_click`, `view_item`, `gadget_interest`, `gadget_share` en Gadgets.
  - `faq_click` para acordeón de preguntas.
- Consulta `docs/analytics/README.md` para la guía completa de configuración en GTM y capturas recomendadas.

## Frontend y experiencia de usuario

- `static/js/portfolio.js` maneja navegación responsive, animaciones de tarjetas, botón “back to top”, lazy loading de imágenes y empuja eventos al `dataLayer`.
- `templates/contact/contactame.html` añade validación de formularios, contador de caracteres, feedback visual y fallback toast tras el envío.
- WhiteNoise sirve archivos estáticos comprimidos en producción (`STATIC_ROOT=staticfiles`).

## Pruebas y verificación

- Ejecuta chequeos básicos de Django: `python manage.py check`.
- Pruebas unitarias (placeholder): `python manage.py test`. Agrega tests en cada app bajo `tests.py` o paquetes dedicados.
- Verifica eventos de analítica con GTM Preview y GA4 DebugView (ver `docs/analytics/`).

## Despliegue en Railway (Docker)

Archivos clave:

- `Dockerfile`: imagen Python 3.13 slim con dependencias de MySQL, `collectstatic` y usuario no-root.
- `start.sh`: aplica migraciones, autocrea superusuario (si variables definidas) y arranca Gunicorn.
- `railway.json`: indica a Railway usar el Dockerfile y ejecutar `./start.sh`.

Pasos sugeridos:

1. Configura variables (`SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS`, `GTM_CONTAINER_ID`/`GA_MEASUREMENT_ID`, `RECAPTCHA_*`, datos de BD).
2. Despliega usando Railway → New Project → Deploy from GitHub → selecciona el repo.
3. Railway construirá la imagen (usa `requirements.txt`), luego iniciará el contenedor ejecutando `start.sh` que corre migraciones + Gunicorn.
4. Accede a `/admin` para gestionar contenido.

## Documentación adicional

- `docs/ERD.md`: diagrama Mermaid del modelo de datos.
- `docs/analytics/README.md`: guía completa de instrumentación GTM/GA4.
- `fixtures/seed.json`: datos iniciales listos para cargar.
- `media/`: carpeta (vacía) para assets subidos desde el admin (`Developer.avatar_image`).

¿Necesitas material para evaluación? Sube URL pública (Railway), repositorio GitHub y un PDF con ERD + capturas del sitio y métricas GA4.
