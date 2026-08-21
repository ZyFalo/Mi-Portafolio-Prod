"""
Traslada al cielo la gente que ya había pasado por el pipeline.

El minijuego cambió de forma, pero las personas que dejaron su marca son las
mismas y no tienen por qué perderla. De cada deploy se conservan el nombre y
el lugar; el hash, el tipo de commit y la duración se quedan por el camino,
porque en un cielo no significan nada.

La tabla se lee con SQL en lugar de con `apps.get_model("pipeline", …)`: así
esta migración no depende de que la app siga instalada y el pipeline se puede
retirar del proyecto sin dejar el historial roto. En una instalación nueva la
tabla no existe y no hay nada que mudar.

Las posiciones se reparten con un patrón determinista y no al azar: una
migración debe dar el mismo resultado cada vez que se aplique.
"""

import math
from datetime import datetime, timezone as zona

from django.db import migrations
from django.utils import timezone

TABLA = "pipeline_deploy"

# Proporción áurea. Repartir ángulos con ella es el truco clásico para
# esparcir puntos sin que formen anillos ni se amontonen.
ANGULO_AUREO = math.pi * (3 - math.sqrt(5))

MARGEN = 0.035


def _posicion(indice, total):
    """Reparte los puntos en espiral desde el centro del lienzo."""
    if total <= 1:
        return 0.5, 0.5

    radio = math.sqrt((indice + 0.5) / total) * 0.38
    angulo = indice * ANGULO_AUREO

    # El lienzo es apaisado (1000x560): sin corregir, la espiral saldría
    # aplastada y las estrellas se pegarían por arriba y por abajo.
    x = 0.5 + math.cos(angulo) * radio
    y = 0.5 + math.sin(angulo) * radio * (1000 / 560) * 0.55

    return (
        min(max(x, MARGEN), 1 - MARGEN),
        min(max(y, MARGEN), 1 - MARGEN),
    )


def _con_zona(momento):
    """
    Devuelve la fecha con zona horaria.

    Leyendo por SQL crudo se pierde lo que el ORM hace por su cuenta: SQLite
    entrega las fechas como texto sin zona y el driver de MySQL las devuelve
    naive. Guardarlas así desplazaría cada estrella varias horas y Django lo
    avisa por consola, no por error.
    """
    if momento is None:
        return timezone.now()
    if isinstance(momento, str):
        momento = datetime.fromisoformat(momento)
    if timezone.is_naive(momento):
        return timezone.make_aware(momento, zona.utc)
    return momento


def deploys_al_cielo(apps, schema_editor):
    Star = apps.get_model("cielo", "Star")
    conexion = schema_editor.connection

    with conexion.cursor() as cursor:
        if TABLA not in conexion.introspection.table_names(cursor):
            # Instalación nueva: nunca hubo pipeline que migrar
            return

        cursor.execute(
            f"SELECT visitor_name, visitor_location, ip_hash, is_visible, created_at "
            f"FROM {TABLA} ORDER BY created_at, id"
        )
        filas = cursor.fetchall()

    if not filas:
        return

    total = len(filas)
    for indice, (nombre, lugar, ip_hash, visible, creado) in enumerate(filas):
        x, y = _posicion(indice, total)
        Star.objects.create(
            name=(nombre or "")[:32] or "Anónimo",
            location=lugar or "",
            x=x,
            y=y,
            # Las estrellas heredadas brillan un punto más: fueron las primeras
            magnitud=2,
            ip_hash=ip_hash or "",
            is_visible=bool(visible),
            created_at=_con_zona(creado),
        )


def vaciar_cielo_heredado(apps, schema_editor):
    """
    Deshace la migración.

    Solo se borran las estrellas que coinciden con un deploy: las encendidas
    después de la mudanza no tienen por qué perderse al volver atrás.
    """
    Star = apps.get_model("cielo", "Star")
    conexion = schema_editor.connection

    with conexion.cursor() as cursor:
        if TABLA not in conexion.introspection.table_names(cursor):
            return
        cursor.execute(f"SELECT visitor_name FROM {TABLA}")
        nombres = [fila[0] for fila in cursor.fetchall() if fila[0]]

    if nombres:
        Star.objects.filter(name__in=nombres).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cielo", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(deploys_al_cielo, vaciar_cielo_heredado),
    ]
