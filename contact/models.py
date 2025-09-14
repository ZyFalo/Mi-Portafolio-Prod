from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=200)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    consent = models.BooleanField(default=False, help_text="Acepto ser contactado por este medio.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"

    def __str__(self) -> str:
        return f"{self.name} <{self.email}> — {self.subject}"


# Create your models here.
