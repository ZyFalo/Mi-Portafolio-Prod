"""
Estado del sistema en vivo.

Todos los valores que se publican aquí son reales: se leen del proceso, del
repositorio y de la base de datos. Nada se simula — la gracia del panel es
justamente que sea verificable.
"""

import os
import platform
import subprocess
import time
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
    Identifica la revisión desplegada.

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


# La revisión no cambia mientras el proceso vive: se resuelve una sola vez.
VERSION = _detectar_version()


def _motor_bd():
    """Nombre legible del motor de base de datos en uso."""
    motor = settings.DATABASES.get("default", {}).get("ENGINE", "")
    return {
        "django.db.backends.sqlite3": "SQLite",
        "django.db.backends.mysql": "MySQL",
        "django.db.backends.postgresql": "PostgreSQL",
    }.get(motor, motor.rsplit(".", 1)[-1] or "desconocido")


def formatear_uptime(segundos):
    """Convierte segundos en una cadena compacta: 3d 4h 12m."""
    segundos = int(segundos)
    dias, resto = divmod(segundos, 86400)
    horas, resto = divmod(resto, 3600)
    minutos = resto // 60

    if dias:
        return f"{dias}d {horas}h {minutos}m"
    if horas:
        return f"{horas}h {minutos}m"
    return f"{minutos}m"


def recolectar():
    """Reúne el estado actual del sistema para publicarlo."""
    activo = time.time() - ARRANQUE

    # El número de deploys de visitantes es un dato real del minijuego
    try:
        from portfolio.apps.pipeline.models import Deploy

        deploys = Deploy.objects.filter(is_visible=True).count()
    except Exception:
        deploys = 0

    return {
        "operativo": True,
        "uptime_segundos": int(activo),
        "uptime": formatear_uptime(activo),
        "arranque": ARRANQUE,
        "version": VERSION,
        "entorno": "producción" if not settings.DEBUG else "local",
        "runtime": f"Python {platform.python_version()}",
        "framework": f"Django {django.get_version()}",
        "servidor": "Gunicorn" if not settings.DEBUG else "runserver",
        "base_datos": _motor_bd(),
        "deploys_visitantes": deploys,
    }
