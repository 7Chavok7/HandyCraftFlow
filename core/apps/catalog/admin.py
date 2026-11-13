# core/apps/catalog/admin.py
from django.contrib import admin
from .models import Category, Product, ProductVariant, PlatformListing


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name", 
        "parent", 
        "depth", 
        "is_active"
    )
    list_filter = (
        "is_active", 
        "depth"
    )
    search_fields = (
        "name", 
        "path"
    )
    readonly_fields = (
        "path", 
        "depth"
    )


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = (
        "name", 
        "color", 
        "vendor_code", 
        "barcode", 
        "extra_cost", 
        "is_active"
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", 
        "category", 
        "is_active"
    )
    list_filter = (
        "is_active", 
        "category"
    )
    search_fields = (
        "name",
        )
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product", 
        "name", 
        "color", 
        "vendor_code", 
        "barcode", 
        "is_active"
    )
    list_filter = (
        "is_active", 
        "color"
    )
    search_fields = (
        "name", 
        "vendor_code", 
        "barcode"
    )


@admin.register(PlatformListing)
class PlatformListingAdmin(admin.ModelAdmin):
    list_display = (
        "variant", 
        "marketplace", 
        "platform_sku", 
        "status"
    )
    list_filter = (
        "marketplace", 
        "status"
    )
    search_fields = (
        "platform_sku", 
        "variant__name", 
        "variant__product__name"
    )