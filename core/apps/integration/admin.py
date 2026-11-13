from django.contrib import admin
from .models import SyncLog


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at", "marketplace", "entity", "status",
        "items_processed", "items_failed",
    )
    list_filter = ("marketplace", "entity", "status")
    readonly_fields = (
        "workspace_id", "marketplace", "entity", "status",
        "items_processed", "items_failed", "error_message",
        "started_at", "finished_at", "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False