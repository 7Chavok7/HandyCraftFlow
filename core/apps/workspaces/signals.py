from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Workspace, WorkspaceSettings


@receiver(post_save, sender=Workspace)
def create_workspace_settings(sender, instance, created, **kwargs):
    if created:
        WorkspaceSettings.objects.get_or_create(workspace=instance)