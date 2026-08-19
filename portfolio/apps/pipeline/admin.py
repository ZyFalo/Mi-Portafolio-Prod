from django.contrib import admin

from .models import Deploy


@admin.register(Deploy)
class DeployAdmin(admin.ModelAdmin):
    list_display = ("commit_hash", "visitor_name", "visitor_location", "message", "is_visible", "created_at")
    list_filter = ("is_visible", "created_at")
    list_editable = ("is_visible",)
    search_fields = ("commit_hash", "visitor_name", "visitor_location", "message")
    readonly_fields = ("commit_hash", "ip_hash", "created_at")
    date_hierarchy = "created_at"
