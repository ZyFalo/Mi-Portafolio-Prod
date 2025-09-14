from django.contrib import admin
from .models import Developer


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "role",
        "is_active",
        "order",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "role", "skills", "banner_name")
    ordering = ("order", "id")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Información básica", {
            "fields": ("name", "role", "bio", "skills", "is_active", "order"),
        }),
        ("Avatar", {
            "fields": ("avatar_image", "avatar_url", "avatar_bg", "avatar_text"),
            "description": "Sube una imagen o usa una URL. Si no hay avatar, se generará con UI-Avatars.",
        }),
        ("Portafolio y Tracking", {
            "fields": ("portfolio_url", "banner_name", "auto_utm", "utm_source", "utm_medium", "utm_campaign"),
        }),
        ("Metadatos", {
            "fields": ("created_at",),
        }),
    )
