# farm/apps/printers/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PrinterViewSet, AmsSlotViewSet, FarmJobViewSet


router = DefaultRouter()
router.register("printers", PrinterViewSet)
router.register("ams-slots", AmsSlotViewSet)
router.register("jobs", FarmJobViewSet)


urlpatterns = [
    path("", include(router.urls)),
]