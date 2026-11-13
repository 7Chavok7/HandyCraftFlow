from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("created_at", "type", "severity", "title", "is_read")
    list_filter = ("type", "severity", "is_read")
    search_fields = ("title", "message")
    readonly_fields = ("created_at",)

    def has_add_permission(self, request):
        return False