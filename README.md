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

#### 1. **Estructura de archivos para Railway:**
- `Dockerfile` - Configuración del contenedor Docker
- `railway.json` - Configuración específica de Railway
- `start.sh` - Script de inicialización automática
- `requirements.txt` - Dependencias Python

#### 2. **Variables de entorno necesarias:**
```bash
# Variables principales (configurar en Railway)
SECRET_KEY=tu-secret-key-super-seguro-aqui
DEBUG=0
ALLOWED_HOSTS=tu-dominio.railway.app
GTM_CONTAINER_ID=GTM-XXXXXXX

# Variables MySQL (Railway las genera automáticamente al crear servicio MySQL)
MYSQL_DATABASE=railway
MYSQL_USER=root
MYSQL_PASSWORD=auto-generado
MYSQL_HOST=containers-us-west-xxx.railway.app
MYSQL_PORT=3306
```

#### 3. **Proceso de despliegue automático:**
1. **Build:** Railway construye la imagen Docker
2. **Migraciones:** `start.sh` ejecuta automáticamente todas las migraciones
3. **Superusuario:** Se crea automáticamente (admin/admin123)
4. **Servidor:** Gunicorn inicia en el puerto asignado por Railway

#### 4. **Acceso a la aplicación:**
- **Web:** `https://tu-dominio.railway.app`
- **Admin:** `https://tu-dominio.railway.app/admin`
  - Usuario: `admin`
  - Contraseña: `admin123`

#### 5. **Base de datos:**
- **Desarrollo:** SQLite (automático)
- **Producción:** MySQL en Railway (opcional)
- **Fallback:** Si MySQL no está configurado, usa SQLite automáticamente

### Configuración MySQL en Railway (opcional):
1. En tu proyecto Railway: **Add Service** → **Database** → **MySQL**
2. Railway genera automáticamente todas las variables `MYSQL_*`
3. Redespliega la aplicación para usar MySQL

### Logs y debugging:
Los logs de Railway mostrarán:
```bash
🚀 Iniciando aplicación Django...
📦 Aplicando migraciones...
👤 Configurando superusuario...
🔍 Verificando base de datos...
🌐 Iniciando servidor en puerto 8000...
```

## Evidencia / Documentación

- ERD en `docs/ERD.md` (exportable a PDF).
- Haz capturas del Admin (FAQs, OpenEntity) y DebugView de GA4.

## Licencia

Uso académico/educativo.

