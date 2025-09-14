from django.db import models
from django.utils.text import slugify
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse, quote


class Developer(models.Model):
    name = models.CharField(max_length=120, verbose_name="Nombre")
    role = models.CharField(max_length=120, verbose_name="Rol/Título")
    bio = models.CharField(max_length=300, verbose_name="Descripción breve")

    # Avatar: se puede subir imagen o usar URL externa (o fallback UI-Avatars)
    avatar_image = models.ImageField(upload_to="developers/", blank=True, null=True, verbose_name="Avatar (imagen)")
    avatar_url = models.URLField(blank=True, verbose_name="Avatar (URL)")
    avatar_bg = models.CharField(max_length=6, blank=True, verbose_name="Fondo avatar HEX",
                                 help_text="Sin #, ej: 4A90E2")
    avatar_text = models.CharField(max_length=6, blank=True, verbose_name="Texto avatar HEX",
                                   help_text="Sin #, ej: ffffff")

    # Portafolio y tracking
    portfolio_url = models.URLField(verbose_name="URL del portafolio")
    banner_name = models.SlugField(max_length=120, blank=True, verbose_name="Nombre de banner",
                                   help_text="Usado para data-banner-name y UTM content")
    auto_utm = models.BooleanField(default=True, verbose_name="Agregar UTM automáticamente")
    utm_source = models.CharField(max_length=60, default="william_portfolio", blank=True)
    utm_medium = models.CharField(max_length=60, default="banner", blank=True)
    utm_campaign = models.CharField(max_length=60, default="dev_network", blank=True)

    # Presentación
    skills = models.CharField(max_length=240, verbose_name="Habilidades",
                              help_text="Separadas por coma, ej: React, TypeScript, Figma")

    # Estado y orden
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Desarrollador"
        verbose_name_plural = "Desarrolladores"

    def __str__(self) -> str:
        return f"{self.name} — {self.role}"

    def save(self, *args, **kwargs):
        if not self.banner_name and self.name:
            # Prefijo para mantener consistencia con el tracking actual
            self.banner_name = f"developer_{slugify(self.name)[:100]}"
        super().save(*args, **kwargs)

    # Helpers para template/admin
    def skills_list(self):
        return [s.strip() for s in (self.skills or "").split(',') if s.strip()]

    @property
    def display_avatar(self) -> str:
        if self.avatar_image:
            return self.avatar_image.url
        if self.avatar_url:
            return self.avatar_url
        # Fallback UI-Avatars
        params = {
            "name": self.name or "Developer",
            "size": "60",
            "bold": "true",
        }
        if self.avatar_bg:
            params["background"] = self.avatar_bg
        if self.avatar_text:
            params["color"] = self.avatar_text
        # Quote name separately to keep proper encoding
        base = "https://ui-avatars.com/api/"
        return f"{base}?{urlencode(params, quote_via=quote)}"

    @property
    def tracked_url(self) -> str:
        url = self.portfolio_url or "#"
        if not self.auto_utm:
            return url
        try:
            parsed = urlparse(url)
            query = dict(parse_qsl(parsed.query))
            # No sobrescribimos si ya existen
            query.setdefault("utm_source", (self.utm_source or "william_portfolio"))
            query.setdefault("utm_medium", (self.utm_medium or "banner"))
            query.setdefault("utm_campaign", (self.utm_campaign or "dev_network"))
            query.setdefault("utm_content", (self.banner_name or slugify(self.name or "developer")))
            new_query = urlencode(query)
            return urlunparse(parsed._replace(query=new_query))
        except Exception:
            return url


# Create your models here.
