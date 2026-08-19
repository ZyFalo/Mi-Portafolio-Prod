from django.contrib import admin
from .models import Tag, OpenEntity


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(OpenEntity)
class OpenEntityAdmin(admin.ModelAdmin):
    list_display = ("title", "icono_previsualizado", "is_published", "created_at")
    list_filter = ("is_published", "keywords")
    list_editable = ("is_published",)
    search_fields = ("title", "summary", "description")
    filter_horizontal = ("keywords",)
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {
            'fields': ("title", "slug", "summary", "description", "image", "icon", "keywords", "is_published")
        }),
        ("Metadatos", {
            'classes': ('collapse',),
            'fields': ("created_at",)
        })
    )
    readonly_fields = ("created_at",)

    @admin.display(description="Icono")
    def icono_previsualizado(self, obj):
        """Muestra qué icono se usará, sea el elegido o el deducido."""
        origen = "elegido" if obj.icon else "automático"
        return f"{obj.icono} ({origen})"


# Register your models here.
