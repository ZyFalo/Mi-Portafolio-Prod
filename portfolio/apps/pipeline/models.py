import hashlib
import re
import secrets

from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .catalogos import BANDERAS, TIPO_POR_DEFECTO, TIPOS_COMMIT

# Un autor de commit se escribe como un identificador, no como un nombre
# propio: sin espacios, igual que en git.
PATRON_AUTOR = r"^[a-zA-Z0-9._\-]{2,24}$"

validar_autor = RegexValidator(
    regex=PATRON_AUTOR,
    message="Usa solo letras, números, punto, guion o guion bajo. Sin espacios.",
)


def quitar_prefijo_tipo(mensaje: str) -> str:
    """
    Elimina un prefijo de tipo escrito a mano dentro del mensaje.

    El tipo ahora viaja en su propio campo, así que un texto como
    'feat: pasé por aquí' se mostraría duplicado ('feat: feat: …'). Esto
    también sanea los deploys guardados antes de que existiera el selector.
    """
    if not mensaje:
        return ""
    tipos = "|".join(re.escape(t) for t, _, _ in TIPOS_COMMIT)
    return re.sub(rf"^\s*(?:{tipos})\s*:\s*", "", mensaje, flags=re.IGNORECASE).strip()


def normalizar_autor(texto: str) -> str:
    """
    Convierte lo que escriba el visitante en un identificador válido.

    'William Andrés' -> 'William-Andres'
    """
    if not isinstance(texto, str):
        return ""

    texto = " ".join(texto.split())

    # Se sustituyen las tildes por su letra base para que el identificador
    # sea seguro en cualquier contexto (URLs, logs, terminal).
    equivalencias = str.maketrans("áàäâãéèëêíìïîóòöôõúùüûñçÁÀÄÂÃÉÈËÊÍÌÏÎÓÒÖÔÕÚÙÜÛÑÇ",
                                  "aaaaaeeeeiiiiooooouuuuncAAAAAEEEEIIIIOOOOOUUUUNC")
    texto = texto.translate(equivalencias)
    texto = texto.replace(" ", "-")
    texto = re.sub(r"[^a-zA-Z0-9._\-]", "", texto)
    texto = re.sub(r"-{2,}", "-", texto).strip("-.")

    return texto[:24]


def generar_commit_hash() -> str:
    """Genera un hash corto estilo commit de git (7 caracteres hex)."""
    return secrets.token_hex(4)[:7]


def hashear_ip(ip: str) -> str:
    """
    Guarda una huella irreversible de la IP para limitar abuso sin
    almacenar datos personales identificables.
    """
    if not ip:
        return ""
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()[:32]


class Deploy(models.Model):
    """
    Un 'despliegue' dejado por un visitante en el pipeline colaborativo.

    Cada visitante lanza su deploy, este recorre las etapas build -> test ->
    deploy y queda registrado en el muro de despliegues del portafolio.
    """

    ETAPAS = ["checkout", "build", "test", "deploy"]

    commit_hash = models.CharField(
        max_length=7,
        unique=True,
        default=generar_commit_hash,
        verbose_name="Hash del commit",
    )
    visitor_name = models.CharField(
        max_length=24,
        validators=[validar_autor],
        verbose_name="Autor del commit",
    )
    visitor_location = models.CharField(
        max_length=32, blank=True, verbose_name="País"
    )
    commit_type = models.CharField(
        max_length=10,
        choices=[(clave, etiqueta) for clave, etiqueta, _ in TIPOS_COMMIT],
        default=TIPO_POR_DEFECTO,
        verbose_name="Tipo de commit",
    )
    message = models.CharField(
        max_length=80, blank=True, verbose_name="Mensaje de commit"
    )
    duration_ms = models.PositiveIntegerField(
        default=0, verbose_name="Duración del pipeline (ms)"
    )
    ip_hash = models.CharField(max_length=32, blank=True, verbose_name="Huella de IP")
    is_visible = models.BooleanField(default=True, verbose_name="Visible en el muro")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha")

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Deploy"
        verbose_name_plural = "Deploys"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["ip_hash", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.commit_hash} — {self.visitor_name}"

    def save(self, *args, **kwargs):
        # El tipo vive en su propio campo: el mensaje no debe repetirlo
        self.message = quitar_prefijo_tipo(self.message)
        super().save(*args, **kwargs)

    @property
    def actor(self) -> str:
        """Identificador estilo git: autor@pais."""
        if self.visitor_location:
            return f"{self.visitor_name}@{self.visitor_location}"
        return self.visitor_name

    @property
    def bandera(self) -> str:
        """Emoji del país, o cadena vacía si no lo indicó."""
        return BANDERAS.get(self.visitor_location, "")

    @property
    def mensaje_limpio(self) -> str:
        """Mensaje sin prefijo, incluidos los registros históricos."""
        return quitar_prefijo_tipo(self.message)

    @property
    def mensaje_convencional(self) -> str:
        """El mensaje en formato Conventional Commits: 'feat: lo que sea'."""
        if not self.mensaje_limpio:
            return ""
        return f"{self.commit_type}: {self.mensaje_limpio}"

    def como_dict(self) -> dict:
        return {
            "commit": self.commit_hash,
            "actor": self.actor,
            "name": self.visitor_name,
            "location": self.visitor_location,
            "flag": self.bandera,
            "type": self.commit_type,
            "message": self.mensaje_limpio,
            "full_message": self.mensaje_convencional,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat(),
        }
