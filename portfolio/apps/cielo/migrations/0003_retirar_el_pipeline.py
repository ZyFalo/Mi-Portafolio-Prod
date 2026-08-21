"""
Retira los restos del pipeline colaborativo.

Va detrás de la mudanza al cielo: para cuando esto se ejecuta, las personas
que habían dejado un deploy ya tienen su estrella. Lo que queda es la tabla
vacía de contenido útil y las filas de una app que ya no está instalada.

Se hace con SQL en lugar de con `DeleteModel` porque el modelo ya no existe
en el proyecto: Django no puede borrar lo que no sabe describir.
"""

from django.db import migrations

TABLA = "pipeline_deploy"


def retirar_tabla(apps, schema_editor):
    conexion = schema_editor.connection

    with conexion.cursor() as cursor:
        if TABLA in conexion.introspection.table_names(cursor):
            cursor.execute(f"DROP TABLE {TABLA}")

        # Sin esto, `showmigrations` seguiría listando una app fantasma. No
        # afecta al funcionamiento, pero deja el historial mintiendo sobre
        # qué hay instalado.
        cursor.execute("DELETE FROM django_migrations WHERE app = %s", ["pipeline"])


def sin_vuelta_atras(apps, schema_editor):
    """
    No se recrea el pipeline.

    Volver atrás aquí significaría reconstruir una tabla cuyo modelo ya no
    está en el código: quedaría vacía y sin nada que la lea. Los datos que
    importaban viven ahora en el cielo, y esa migración sí se puede revertir.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("cielo", "0002_migrar_deploys_a_estrellas"),
    ]

    operations = [
        migrations.RunPython(retirar_tabla, sin_vuelta_atras),
    ]
