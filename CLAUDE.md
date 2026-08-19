# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django 5.0.7 portfolio site (Spanish-language) with five modular apps: home/developer network, contact form, FAQ, gadgets/setups gallery, and analytics. Content is managed via Django Admin. Deployed on Railway with Docker.

## Common Commands

```bash
# Local setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt   # local deps (no mysqlclient)
pip install -r requirements.txt       # production deps (includes mysqlclient)

# Database
python manage.py migrate
python manage.py loaddata fixtures/seed.json   # sample data (7 FAQ, 6 gadgets, dev data)

# Run
python manage.py runserver              # uses portfolio.settings.local (DEBUG=True)
DEBUG=0 SECRET_KEY=x python manage.py runserver --settings=portfolio.settings.production

# Checks
python manage.py check
python manage.py test                                  # all apps (tests are currently stubs)
python manage.py test portfolio.apps.core              # single app
python manage.py test portfolio.apps.contact.tests     # single test module

# Static files (required after CSS/JS changes for production)
python manage.py collectstatic --noinput

# Custom management commands
python manage.py createsuperuserzyfalo    # creates fixed superuser (zyfalo/admin123)

# Docker
docker build -t mi-portafolio .
docker run -e DEBUG=0 -e SECRET_KEY=your-key -p 8000:8000 mi-portafolio
```

## Architecture

### Settings split
`portfolio/settings/base.py` (shared) → `local.py` (DEBUG=True, SQLite) and `production.py` (DEBUG=False, SSL proxy headers). `manage.py` defaults to `portfolio.settings.local`; `wsgi.py`/`asgi.py` default to `portfolio.settings.production`.

### Dependencies
`requirements-base.txt` (Django, WhiteNoise, Pillow, dj-database-url) → `requirements-dev.txt` (includes base, no MySQL/Gunicorn) and `requirements.txt` (production: adds mysqlclient + gunicorn independently).

### Database resolution order
1. `DATABASE_URL` env var (via `dj-database-url`)
2. Explicit `MYSQL_*` env vars
3. SQLite fallback (`db.sqlite3`)

### Apps (`portfolio/apps/`)
- **core** — Home page with `Developer` model. Auto-generates UTM tracking URLs per developer (`tracked_url` property). Views: `home`.
- **contact** — `ContactMessage` model. Form has honeypot field (`website`), timestamp validation (>1500ms), and optional reCAPTCHA v2. Anti-bot logic lives in `forms.py` + `views.py`.
- **faq** — `Question` model with auto-slug, ordering, `is_active` flag. View: `fyq`.
- **openapp** — `OpenEntity` + `Tag` (M2M). Gadgets grid and slug-based detail. Views: `open_list`, `open_detail`.
- **analytics** — Context processor only (no models). Injects `GTM_CONTAINER_ID`, `GA_MEASUREMENT_ID`, reCAPTCHA keys into all templates.

### URL routes (`portfolio/urls.py`)
`/` home · `/contactame/` contact · `/fyq/` FAQ · `/open/` gadgets list · `/open/<slug>/` gadget detail · `/admin/` Django Admin

### Frontend
- Bootstrap 5.3 + Bootstrap Icons via CDN (loaded in `templates/base.html`)
- All app templates extend `templates/base.html`
- `static/js/portfolio.js` — nav toggle, smooth scroll, mobile detection, dataLayer event pushing
- `static/css/portfolio.css` — Bootstrap overrides, CSS custom properties (`--bg-main`, `--primary`, etc.)
- `staticfiles/` — output of `collectstatic` (WhiteNoise `CompressedManifestStaticFilesStorage`), **never edit directly**

### Analytics (GTM/GA4)
- `templates/base.html` initializes `window.dataLayer` with `page_view` + UTM params
- Falls back to `gtag` if no GTM container ID is set
- Key events: `developer_portfolio_click`, `contact_form_submit`, `generate_lead`, `view_item_list`, `gadget_click`, `view_item`, `faq_click`
- Full instrumentation guide: `docs/analytics/README.md`

### Production flow (Docker/Railway)
`Dockerfile` (Python 3.12-slim) → `docker/entrypoint.sh` → `start.sh` (migrations + superuser creation + Gunicorn with 3 workers). `railway.json` configures Railway to use the Dockerfile builder.

**Note:** `start.sh` creates a hardcoded superuser `zyfalo`/`admin123` on every startup — review before real production use.

## Guardrails

- Do not edit `staticfiles/` — run `collectstatic` instead
- Preserve the `dataLayer` initialization and GA4 events in `templates/base.html`
- Do not remove anti-bot fields (`website` honeypot, `ts` timestamp) from the contact form or its validation
- If changing HTML layout, verify that element IDs/anchors referenced by `portfolio.js` still exist
- Avoid duplicating `page_view` — either GTM handles it automatically or the custom event does, not both
- Model changes require running `makemigrations` + `migrate`
- Analytics changes should be reflected in `docs/analytics/README.md`

## Environment Variables

See `.env.example` for the full list. Key variables: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL` (or `MYSQL_*`), `GTM_CONTAINER_ID`, `GA_MEASUREMENT_ID`, `RECAPTCHA_SITE_KEY`, `RECAPTCHA_SECRET_KEY`, `RECAPTCHA_ENABLED`, `PORT`, `DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD`.

## Language & Conventions

- Codebase documentation and commit messages are in **Spanish**
- Models: PascalCase. Views/functions: snake_case. Apps: lowercase
- Slugs are auto-generated via Django's `slugify()`
- All models are registered in their app's `admin.py` for Django Admin management

## Additional Documentation

- `docs/ERD.md` — Entity relationship diagram (Mermaid)
- `docs/analytics/README.md` — GTM/GA4 instrumentation guide
- `AGENTS.md` — Operational guide for agents/contributors
