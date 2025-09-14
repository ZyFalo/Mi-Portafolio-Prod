# Portafolio Django — Gadgets & Setups

Proyecto de portafolio con Django + Admin como CMS. Incluye:

- Home con CV y 2 banners con UTM.
- Formulario de contacto con validación, honeypot y timestamp anti‑bot.
- FYQ administrables con acordeón accesible.
- "Open" = Gadgets & Setups: grid + detalle, imagen, resumen, descripción y keywords.
- Integración de Google Tag Manager con eventos personalizados.

## Stack

- Django 5 + SQLite
- Tailwind por CDN (rápido para prototipo)
- WhiteNoise para estáticos en producción

## Arranque local

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python manage.py migrate
python manage.py loaddata fixtures/seed.json
python manage.py createsuperuser
python manage.py runserver
```

Abrir: http://127.0.0.1:8000 y http://127.0.0.1:8000/admin/

## Variables de entorno

- `SECRET_KEY`: secreto de Django
- `DEBUG`: 0/1
- `ALLOWED_HOSTS`: dominios separados por coma
- `GTM_CONTAINER_ID`: ID de contenedor GTM (GTM-XXXX)
- `GA_MEASUREMENT_ID` (opcional si usas GTM con GA4 dentro)

## Estructura de apps

- `core`: Home (CV + banners UTM)
- `contact`: Formulario de contacto (`ContactMessage`)
- `faq`: Preguntas frecuentes (`Question`)
- `openapp`: Gadgets & Setups (`OpenEntity`, `Tag`)
- `analytics`: context processor para inyectar IDs de GTM/GA

## Modelos (CMS)

- `faq.Question(title, slug, answer, order, is_active)`
- `openapp.Tag(name, slug)`
- `openapp.OpenEntity(title, slug, summary, description, image, keywords[M2M Tag], created_at, is_published)`
- `contact.ContactMessage(name, email, subject, message, consent, created_at)`

## Analítica (GTM + GA4)

1. En GTM, crea contenedor web y añade tag "GA4 Configuration" con tu `GA_MEASUREMENT_ID`.
2. Publica el contenedor y pon `GTM_CONTAINER_ID` en tu `.env`/config del hosting.
3. Eventos automarcados desde el sitio:
   - Clic en banners del Home: `dataLayer.push({event:'banner_click', banner_name:'compa_1'})`
   - Envío correcto del contacto: `dataLayer.push({event:'contact_submit', form:'contactame', status:'success'})`
4. Verificación: usa DebugView de GA4 + Reporte de Adquisición para ver UTM.

## Despliegue (Render/Railway)

- Usa `requirements.txt`, `Procfile` y `runtime.txt`.
- Ajusta variables: `SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS`, `GTM_CONTAINER_ID`.
- Activa build command opcional de estáticos: `python manage.py collectstatic --noinput`.
- WhiteNoise sirve `STATICFILES` sin necesidad de Nginx adicional.

## Evidencia / Documentación

- ERD en `docs/ERD.md` (exportable a PDF).
- Haz capturas del Admin (FAQs, OpenEntity) y DebugView de GA4.

## Licencia

Uso académico/educativo.

