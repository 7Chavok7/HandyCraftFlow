# farm/farm/urls.py
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("farm/api/v1/", include("apps.printers.urls")),
]