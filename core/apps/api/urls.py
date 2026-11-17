from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.api.views import (
    guide, catalog, materials, production, warehouse, pricing, promo, alerts,
)
from apps.api.views import auth as auth_views
from apps.api.views.dashboard import TodayDashboardView, VariantEconomicsView, CurrentWorkspaceView
from apps.api.views import workspaces as workspace_views


router = DefaultRouter()

# guide
router.register("units", guide.UnitViewSet)
router.register("colors", guide.ColorViewSet)
router.register("countries", guide.CountryViewSet)
router.register("manufacturers", guide.ManufacturerViewSet)

# catalog
router.register("categories", catalog.CategoryViewSet)
router.register("products", catalog.ProductViewSet)
router.register("variants", catalog.ProductVariantViewSet)
router.register("listings", catalog.PlatformListingViewSet)

# materials
router.register("materials", materials.MaterialTypeViewSet, basename="material")
router.register("batches", materials.MaterialBatchViewSet)
router.register("material-ledger", materials.MaterialLedgerViewSet, basename="material-ledger")

# production
router.register("profiles", production.ProductionProfileViewSet)
router.register("assets", production.ProductionAssetViewSet)
router.register("recipes", production.RecipeViewSet)
router.register("recipe-lines", production.RecipeLineViewSet)
router.register("jobs", production.ProductionJobViewSet)

# warehouse
router.register("accounts", warehouse.SellerAccountViewSet)
router.register("warehouses", warehouse.WarehouseViewSet)
router.register("stocks", warehouse.StockViewSet)
router.register("stock-ledger", warehouse.StockLedgerViewSet, basename="stock-ledger")

# pricing
router.register("price-rules", pricing.PriceRuleViewSet)
router.register("price-history", pricing.PriceHistoryViewSet, basename="price-history")
router.register("fees", pricing.MarketplaceFeeViewSet)

# promo
router.register("promotions", promo.PromotionViewSet)
router.register("promotion-items", promo.PromotionItemViewSet)

# alerts
router.register("alerts", alerts.AlertViewSet)

# workspace
router.register("settings", workspace_views.WorkspaceSettingsViewSet, basename="settings")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", auth_views.LoginView.as_view(), name="auth-login"),
    path("auth/logout/", auth_views.LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", auth_views.MeView.as_view(), name="auth-me"),
    path("dashboard/today/", TodayDashboardView.as_view(), name="dashboard-today"),
    path("dashboard/economics/", VariantEconomicsView.as_view(), name="dashboard-economics"),
    path("me/workspace/", CurrentWorkspaceView.as_view(), name="me-workspace"),
    path("auth/csrf/", auth_views.CsrfTokenView.as_view(), name="auth-csrf"),
]