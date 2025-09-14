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

1. En GTM, crea contenedor web y añade tag "GA4 Configuration" con tu Measurement ID.
2. Publica el contenedor y pon `GTM_CONTAINER_ID` en tu `.env`/config del hosting.
3. Eventos automarcados desde el sitio:
   - Clic en banners del Home: `dataLayer.push({event:'banner_click', banner_name:'compa_1'})`
   - Envío correcto del contacto: `dataLayer.push({event:'contact_submit', form:'contactame', status:'success'})`
4. Verificación: usa DebugView de GA4 + Reporte de Adquisición para ver UTM.

## Despliegue en Railway (Docker + MySQL)

### Configuración local:
```bash
python manage.py runserver
```

### Despliegue en Railway:

1. **Crear servicios en Railway:**
   - Servicio MySQL (Database)
   - Servicio Web (tu aplicación Docker)

2. **Variables de entorno a configurar en Railway:**
   ```
   SECRET_KEY=tu-secret-key-super-seguro-aqui
   DEBUG=0
   ALLOWED_HOSTS=tu-dominio.railway.app
   GTM_CONTAINER_ID=GTM-XXXXXXX
   
   # Variables de MySQL (se generan automáticamente al crear el servicio MySQL)
   MYSQL_DATABASE=railway
   MYSQL_USER=root
   MYSQL_PASSWORD=auto-generado-por-railway
   MYSQL_HOST=containers-us-west-xxx.railway.app
   MYSQL_PORT=3306
   RAILWAY_ENVIRONMENT=production
   ```

3. **Puerto de la aplicación:**
   - Railway asigna automáticamente el puerto via variable `PORT`
   - La aplicación escucha en el puerto 8000 internamente
   - Acceso público: `https://tu-dominio.railway.app`

4. **Proceso de despliegue:**
   - Railway detecta automáticamente el `Dockerfile`
   - Construye la imagen Docker
   - Ejecuta migraciones y collectstatic automáticamente
   - Despliega la aplicación

### Comandos útiles para Railway:
```bash
# Ejecutar migraciones (se hace automáticamente)
python manage.py migrate

# Crear superusuario (via Railway CLI)
railway run python manage.py createsuperuser
```

## Evidencia / Documentación

- ERD en `docs/ERD.md` (exportable a PDF).
- Haz capturas del Admin (FAQs, OpenEntity) y DebugView de GA4.

## Licencia

Uso académico/educativo.

