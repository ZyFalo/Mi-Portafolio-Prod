from django.contrib import admin

from .models import Star


@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "magnitud", "created_at", "is_visible")
    list_filter = ("is_visible", "location")
    search_fields = ("name", "location")
    ordering = ("-created_at",)
    readonly_fields = ("ip_hash", "created_at")
    fieldsets = (
        ("Visitante", {"fields": ("name", "location")}),
        (
            "Posición en el cielo",
            {
                "fields": ("x", "y", "magnitud"),
                "description": "Coordenadas normalizadas entre 0 y 1.",
            },
        ),
        (
            "Moderación",
            {
                "fields": ("is_visible", "ip_hash", "created_at"),
                "description": "Desmarca «visible» para retirar una estrella del cielo sin borrarla.",
            },
        ),
    )
