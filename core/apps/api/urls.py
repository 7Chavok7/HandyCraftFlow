from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.api.views import guide, catalog
from apps.api.views.dashboard import TodayDashboardView, VariantEconomicsView


router = DefaultRouter()
router.register("units", guide.UnitViewSet)
router.register("colors", guide.ColorViewSet)
router.register("countries", guide.CountryViewSet)
router.register("manufacturers", guide.ManufacturerViewSet)
router.register("categories", catalog.CategoryViewSet)
router.register("products", catalog.ProductViewSet)
router.register("variants", catalog.ProductVariantViewSet)
router.register("listings", catalog.PlatformListingViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/today/", TodayDashboardView.as_view(), name="dashboard-today"),
    path("dashboard/economics/", VariantEconomicsView.as_view(), name="dashboard-economics"),
]