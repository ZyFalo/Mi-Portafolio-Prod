import hashlib
import random
import re
import unicodedata

from django.db import models
from django.utils import timezone

from .catalogos import BANDERAS

# Un nombre humano, no un identificador de git: se admiten espacios, tildes,
# apóstrofos y guiones, que es como se escribe la gente de verdad.
CARACTERES_NOMBRE = re.compile(r"[^\w\s.\-']", flags=re.UNICODE)

LARGO_MINIMO = 2
LARGO_MAXIMO = 32

# Cada estrella recibe un tamaño al nacer. Un cielo donde todas brillan igual
# se lee como una cuadrícula; la variedad es lo que lo hace parecer un cielo.
MAGNITUDES = (1, 1, 1, 2, 2, 3)


def limpiar_nombre(texto: str) -> str:
    """
    Deja el nombre listo para mostrarse, sin desfigurarlo.

    A diferencia del pipeline, que exigía un identificador sin espacios,
    aquí "Ana María" o "O'Brien" se conservan tal cual: el cielo lo firma
    cualquiera, no solo quien esté acostumbrado a la consola.
    """
    if not isinstance(texto, str):
        return ""

    # Los caracteres de control y los invisibles se van antes que nada
    texto = "".join(c for c in texto if unicodedata.category(c)[0] != "C")
    texto = CARACTERES_NOMBRE.sub("", texto)
    texto = " ".join(texto.split())

    return texto[:LARGO_MAXIMO].strip(" .-'")


def hashear_ip(ip: str) -> str:
    """
    Guarda una huella irreversible de la IP para limitar abuso sin
    almacenar datos personales identificables.
    """
    if not ip:
        return ""
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()[:32]


def magnitud_al_azar() -> int:
    return random.choice(MAGNITUDES)


class Star(models.Model):
    """
    Una estrella encendida por un visitante.

    El cielo es la aportación colectiva del portafolio: cada persona que pasa
    elige un punto y deja su nombre. Las coordenadas se guardan normalizadas
    entre 0 y 1 —no en píxeles— para que el mismo cielo se vea igual en un
    móvil que en un monitor ancho.
    """

    name = models.CharField(max_length=LARGO_MAXIMO, verbose_name="Nombre")
    location = models.CharField(max_length=32, blank=True, verbose_name="Lugar")

    x = models.FloatField(verbose_name="Posición X", help_text="Entre 0 y 1")
    y = models.FloatField(verbose_name="Posición Y", help_text="Entre 0 y 1")
    magnitud = models.PositiveSmallIntegerField(
        default=magnitud_al_azar, verbose_name="Tamaño"
    )

    ip_hash = models.CharField(max_length=32, blank=True, verbose_name="Huella de IP")
    is_visible = models.BooleanField(default=True, verbose_name="Visible en el cielo")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Encendida el")

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Estrella"
        verbose_name_plural = "Estrellas"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["ip_hash", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} — {self.location or 'sin lugar'}"

    @property
    def bandera(self) -> str:
        """Emoji del país, o cadena vacía si no lo indicó."""
        return BANDERAS.get(self.location, "")

    @property
    def etiqueta(self) -> str:
        """Cómo se presenta la estrella al pasar por encima."""
        if self.location:
            return f"{self.name} · {self.location}"
        return self.name

    def como_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "flag": self.bandera,
            "label": self.etiqueta,
            "x": round(self.x, 5),
            "y": round(self.y, 5),
            "magnitud": self.magnitud,
            "created_at": self.created_at.isoformat(),
        }
