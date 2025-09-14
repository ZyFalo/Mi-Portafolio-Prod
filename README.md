# Portafolio Django — Gadgets & Setups

Proyecto de portafolio con Django + Admin como CMS. Cumple con:

- Home con CV, red de desarrolladores (banners) con UTM.
- Formulario de contacto validado con JavaScript y guardado en el CMS.
- Preguntas frecuentes (FAQ) administrables con UI expandible/colapsable.
- Página Open (Gadgets & Setups) con grid, imagen, resumen, descripción y tags.
- Integración con Google Tag Manager (GTM) y eventos hacia GA4.

## Stack

- Django 5 + SQLite (dev)
- Bootstrap por CDN
- WhiteNoise para estáticos en producción

## Uso local

```bash
python -m venv .venv
. .venv/Scripts/activate  # PowerShell: .\.venv\Scripts\Activate.ps1

# Instala dependencias para desarrollo (sin mysqlclient)
pip install -r requirements-dev.txt

python manage.py migrate
python manage.py loaddata fixtures/seed.json  # opcional
python manage.py createsuperuser
python manage.py runserver
```

Abrir: http://127.0.0.1:8000 y http://127.0.0.1:8000/admin/

## Variables de entorno

- `SECRET_KEY`: secreto de Django
- `DEBUG`: 0/1 (por defecto 1 en dev)
- `ALLOWED_HOSTS`: dominios separados por coma
- `CSRF_TRUSTED_ORIGINS`: orígenes completos separados por coma (https://dominio)
- `GTM_CONTAINER_ID`: ID de contenedor GTM (GTM-XXXX)

## Estructura de apps

- `core`: Home (CV + red de desarrolladores con UTM)
- `contact`: Formulario de contacto (`ContactMessage`)
- `faq`: Preguntas frecuentes (`Question`)
- `openapp`: Gadgets & Setups (`OpenEntity`, `Tag`)
- `analytics`: context processor para inyectar IDs de GTM/GA

## Modelos (CMS)

- `faq.Question(title, slug, answer, order, is_active)`
- `openapp.Tag(name, slug)`
- `openapp.OpenEntity(title, slug, summary, description, image, keywords[M2M Tag], created_at, is_published)`
- `contact.ContactMessage(name, email, subject, message, consent, created_at)`
- `core.Developer(name, role, bio, avatar_image/url, skills, portfolio_url, utm_*, banner_name, is_active, order)`

## Analítica (GTM + GA4)

1. En GTM, crea contenedor web y añade tag "GA4 Configuration" con tu Measurement ID.
2. Publica el contenedor y pon `GTM_CONTAINER_ID` en Railway/entorno.
3. Eventos desde el sitio (ejemplos):
   - Clic en card de desarrollador: `developer_portfolio_click`
   - Envío de contacto: `contact_form_submit`
   - Clic en gadget/lista: `gadget_click`

## Despliegue en Railway (Docker)

Archivos relevantes:

- `Dockerfile` — Imagen con dependencias y collectstatic
- `railway.json` — Define builder dockerfile y start command
- `start.sh` — Aplica migraciones y levanta Gunicorn
- `requirements.txt` — Producción (incluye `mysqlclient` y `gunicorn`)
- `requirements-dev.txt` — Desarrollo local (sin `mysqlclient`)

Variables recomendadas en Railway:

```bash
SECRET_KEY=tu-secret
DEBUG=0
ALLOWED_HOSTS=tu-dominio.railway.app
GTM_CONTAINER_ID=GTM-XXXXXXX

# Opción A: usar DATABASE_URL
DATABASE_URL=mysql://user:pass@host:3306/dbname

# Opción B: usar variables MYSQL_*
MYSQL_DATABASE=railway
MYSQL_USER=root
MYSQL_PASSWORD=...
MYSQL_HOST=...
MYSQL_PORT=3306

# (Opcional) crear superusuario al iniciar
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

Proceso:

1) Railway construye la imagen Docker (usa `requirements.txt`).
2) El contenedor ejecuta `start.sh` (migraciones + Gunicorn).
3) Accede a `/admin` para gestionar contenido (FAQ, Open, Contact, Developers).

## Entregables sugeridos

- URL pública en Railway
- Repositorio GitHub
- PDF con ERD (`docs/ERD.md`), capturas del sitio y capturas de GA4/GTM

