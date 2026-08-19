from django.db import models
from django.utils.text import slugify
from django.urls import reverse

# Iconos disponibles para los gadgets (Bootstrap Icons, ya cargado en base).
# Se ofrece una lista cerrada para que el desplegable del admin sea usable y
# no haya que recordar nombres de iconos de memoria.
ICONOS = [
    ("", "Automático (según el título)"),
    ("lightbulb", "💡 Iluminación / lámpara"),
    ("display", "🖥 Monitor / pantalla"),
    ("keyboard", "⌨ Teclado"),
    ("mouse", "🖱 Ratón"),
    ("mic", "🎙 Micrófono"),
    ("headphones", "🎧 Auriculares"),
    ("camera-video", "📹 Cámara / webcam"),
    ("usb-symbol", "🔌 Hub / adaptador USB"),
    ("plug", "🔋 Cable / cargador"),
    ("person-workspace", "🪑 Silla / escritorio"),
    ("laptop", "💻 Portátil"),
    ("pc-display", "🖲 Equipo de sobremesa"),
    ("device-hdd", "💾 Almacenamiento / SSD"),
    ("router", "📡 Router / red"),
    ("speaker", "🔊 Altavoces"),
    ("smartwatch", "⌚ Wearable"),
    ("phone", "📱 Móvil"),
    ("tablet", "📓 Tableta"),
    ("book", "📗 Libro"),
    ("mortarboard", "🎓 Curso / formación"),
    ("cup-hot", "☕ Café / escritorio"),
    ("tools", "🛠 Herramienta"),
    ("box-seam", "📦 Genérico"),
]


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:60]
        super().save(*args, **kwargs)


class OpenEntity(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    summary = models.CharField(max_length=240)
    description = models.TextField(help_text="Puedes usar HTML básico para formato.")
    image = models.URLField(blank=True, null=True, verbose_name="Imagen (URL)")
    icon = models.CharField(
        max_length=30,
        blank=True,
        choices=ICONOS,
        verbose_name="Icono",
        help_text="Si lo dejas en automático, se deduce del título del gadget.",
    )
    keywords = models.ManyToManyField(Tag, related_name="items", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Producto/Setup"
        verbose_name_plural = "Productos/Setups"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("open_detail", args=[self.slug])

    @property
    def icono(self) -> str:
        """
        Icono a mostrar en la tarjeta.

        Manda lo elegido en el admin; si se dejó en automático, se deduce del
        título y las etiquetas para que un gadget nuevo nunca quede sin icono.
        """
        if self.icon:
            return self.icon

        # El orden importa: se comprueba de más específico a más genérico.
        # "Micrófono USB" debe dar micrófono, no hub USB.
        pistas = [
            # Dispositivos concretos primero
            ("microfono", "mic"), ("micrófono", "mic"), ("podcast", "mic"),
            ("auricular", "headphones"), ("audifono", "headphones"),
            ("audífono", "headphones"), ("headset", "headphones"),
            ("teclado", "keyboard"), ("keychron", "keyboard"), ("keyboard", "keyboard"),
            ("monitor", "display"), ("pantalla", "display"), ("display", "display"),
            ("camara", "camera-video"), ("cámara", "camera-video"), ("webcam", "camera-video"),
            ("altavoz", "speaker"), ("altavoces", "speaker"), ("parlante", "speaker"),
            ("lampara", "lightbulb"), ("lámpara", "lightbulb"),
            ("iluminacion", "lightbulb"), ("iluminación", "lightbulb"),
            ("silla", "person-workspace"), ("ergonom", "person-workspace"),
            ("escritorio", "person-workspace"),
            ("portatil", "laptop"), ("portátil", "laptop"), ("laptop", "laptop"),
            ("mouse", "mouse"), ("raton", "mouse"), ("ratón", "mouse"),
            ("ssd", "device-hdd"), ("disco", "device-hdd"), ("almacenamiento", "device-hdd"),
            ("router", "router"),
            ("cargador", "plug"), ("bateria", "plug"), ("batería", "plug"),
            ("libro", "book"), ("curso", "mortarboard"),
            # Términos amplios al final: solo actúan si nada anterior encajó
            ("hub", "usb-symbol"), ("adaptador", "usb-symbol"), ("usb", "usb-symbol"),
            ("cable", "plug"), ("luz", "lightbulb"), ("audio", "mic"),
            ("red", "router"),
        ]

        texto = self.title.lower()
        try:
            texto += " " + " ".join(t.name.lower() for t in self.keywords.all())
        except ValueError:
            # El objeto aún no tiene pk: todavía no hay etiquetas que consultar
            pass

        for palabra, icono in pistas:
            if palabra in texto:
                return icono

        return "box-seam"


# Create your models here.
