from django.db import models
from django.utils.text import slugify
from django.urls import reverse


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


# Create your models here.
