"""
Estado del sistema en vivo.

Todos los valores que se publican aquí son reales: se leen del proceso, del
repositorio y de la base de datos. Nada se simula — la gracia del panel es
justamente que sea verificable.

La versión en producción es la del último deploy del pipeline colaborativo:
el panel describe la aplicación que construyen los visitantes, servida sobre
la infraestructura real de este portafolio.
"""

import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import django
from django.conf import settings

# Momento en que arrancó el proceso (se fija al importar el módulo)
ARRANQUE = time.time()

RAIZ = Path(settings.BASE_DIR)


def _git(*argumentos):
    """Ejecuta un comando git en el repositorio; devuelve '' si no es posible."""
    try:
        salida = subprocess.run(
            ["git", *argumentos],
            cwd=str(RAIZ),
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if salida.returncode == 0:
            return salida.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


def _detectar_version():
    """
    Identifica la revisión del repositorio que sirve el sitio.

    Es el commit inicial del sistema: a partir de ahí, quien manda en el panel
    son los deploys que dejan los visitantes.

    En Railway el repositorio no viaja en la imagen, así que se prefieren las
    variables de entorno que la plataforma inyecta durante el build.
    """
    sha = (
        os.environ.get("RAILWAY_GIT_COMMIT_SHA")
        or os.environ.get("GIT_COMMIT_SHA")
        or _git("rev-parse", "HEAD")
    )
    fecha = os.environ.get("BUILD_TIMESTAMP", "") or _git("log", "-1", "--format=%cI")
    rama = (
        os.environ.get("RAILWAY_GIT_BRANCH")
        or _git("rev-parse", "--abbrev-ref", "HEAD")
    )
    asunto = os.environ.get("GIT_COMMIT_MESSAGE", "") or _git("log", "-1", "--format=%s")

    return {
        "commit": sha[:7] if sha else "",
        "rama": rama,
        "fecha": fecha,
        "asunto": asunto[:72],
    }


# El repositorio no cambia mientras el proceso vive: se resuelve una sola vez.
VERSION = _detectar_version()


def _fecha_respaldo():
    """
    Fecha del commit inicial, para cuando todavía no hay deploys de visitantes.

    Se busca por orden de fidelidad: la fecha real del último commit (solo
    disponible donde viaja el repositorio, es decir en local), el sello que el
    Dockerfile escribe durante el build, y una variable de entorno.
    """
    candidatos = [VERSION.get("fecha", ""), os.environ.get("BUILD_TIMESTAMP", "")]

    sello = RAIZ / "BUILD_TIME"
    try:
        if sello.is_file():
            candidatos.insert(1, sello.read_text(encoding="utf-8").strip())
    except OSError:
        pass

    for texto_fecha in candidatos:
        if not texto_fecha:
            continue
        try:
            momento = datetime.fromisoformat(texto_fecha.replace("Z", "+00:00"))
            if momento.tzinfo is None:
                momento = momento.replace(tzinfo=timezone.utc)
            return momento.timestamp()
        except ValueError:
            continue

    return None


def _revision_en_produccion():
    """
    Revisión que el panel declara en producción.

    El sistema que describe este panel no es el repositorio del portafolio,
    sino la aplicación que se construye entre todos: cada visitante que lanza
    su pipeline publica una versión nueva, y esa pasa a ser la que está en
    producción. Mientras nadie haya desplegado se muestra la revisión del
    repositorio, que hace las veces de commit inicial.
    """
    try:
        from portfolio.apps.pipeline.models import Deploy

        # El modelo ya ordena por fecha descendente y tiene índice para ello
        ultimo = Deploy.objects.filter(is_visible=True).first()
    except Exception:
        # Sin base de datos todavía (migraciones, collectstatic)
        ultimo = None

    if ultimo is None:
        return {
            "commit": VERSION.get("commit", ""),
            "rama": VERSION.get("rama", ""),
            "autor": "",
            "asunto": VERSION.get("asunto", ""),
            "momento": _fecha_respaldo(),
            "inicial": True,
        }

    return {
        "commit": ultimo.commit_hash,
        "rama": VERSION.get("rama", ""),
        "autor": ultimo.actor,
        "asunto": ultimo.mensaje_convencional,
        "momento": ultimo.created_at.timestamp(),
        "inicial": False,
    }


def _motor_bd():
    """Nombre legible del motor de base de datos en uso."""
    motor = settings.DATABASES.get("default", {}).get("ENGINE", "")
    return {
        "django.db.backends.sqlite3": "SQLite",
        "django.db.backends.mysql": "MySQL",
        "django.db.backends.postgresql": "PostgreSQL",
    }.get(motor, motor.rsplit(".", 1)[-1] or "desconocido")


def formatear_uptime(segundos):
    """
    Convierte segundos en una cadena compacta: 3d 4h 12m, 2h 5m 30s, 40s.

    El formato es el mismo que usa formatearUptime() en efectos.js: los relojes
    siguen contando en el navegador y no deben dar un salto al tomar el relevo.
    """
    segundos = max(0, int(segundos))
    dias, resto = divmod(segundos, 86400)
    horas, resto = divmod(resto, 3600)
    minutos, restantes = divmod(resto, 60)

    if dias:
        return f"{dias}d {horas}h {minutos}m"
    if horas:
        return f"{horas}h {minutos}m {restantes}s"
    if minutos:
        return f"{minutos}m {restantes}s"
    return f"{restantes}s"


def recolectar():
    """Reúne el estado actual del sistema para publicarlo."""
    activo = time.time() - ARRANQUE

    # El número de deploys de visitantes es un dato real del minijuego
    try:
        from portfolio.apps.pipeline.models import Deploy

        deploys = Deploy.objects.filter(is_visible=True).count()
    except Exception:
        deploys = 0

    # Antigüedad de la versión publicada: solo cambia cuando alguien despliega
    revision = _revision_en_produccion()
    despliegue = revision["momento"]
    if despliegue:
        desde_despliegue = max(0, time.time() - despliegue)
        desplegado = formatear_uptime(desde_despliegue)
    else:
        desde_despliegue = None
        desplegado = "—"

    return {
        "operativo": True,
        # Tiempo del proceso: se pone a cero en cada reinicio del contenedor
        "uptime_segundos": int(activo),
        "uptime": formatear_uptime(activo),
        "arranque": ARRANQUE,
        # Tiempo desde el último deploy publicado en el muro
        "despliegue": despliegue,
        "desplegado_segundos": int(desde_despliegue) if desde_despliegue else None,
        "desplegado": desplegado,
        "version": {
            "commit": revision["commit"],
            "rama": revision["rama"],
            "autor": revision["autor"],
            "asunto": revision["asunto"],
        },
        "entorno": "producción" if not settings.DEBUG else "local",
        "runtime": f"Python {platform.python_version()}",
        "framework": f"Django {django.get_version()}",
        "servidor": "Gunicorn" if not settings.DEBUG else "runserver",
        "base_datos": _motor_bd(),
        "deploys_visitantes": deploys,
    }
