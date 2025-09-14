from django.contrib import admin
from .models import Tag, OpenEntity


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(OpenEntity)
class OpenEntityAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "created_at")
    list_filter = ("is_published", "keywords")
    list_editable = ("is_published",)
    search_fields = ("title", "summary", "description")
    filter_horizontal = ("keywords",)
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {
            'fields': ("title", "slug", "summary", "description", "image", "keywords", "is_published")
        }),
        ("Metadatos", {
            'classes': ('collapse',),
            'fields': ("created_at",)
        })
    )
    readonly_fields = ("created_at",)


# Register your models here.
