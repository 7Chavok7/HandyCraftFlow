# core/apps/guide/admin.py
from django.contrib import admin
from .models import Unit, Color, Country, Manufacturer


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = (
        "name", 
        "short_name"
    )
    search_fields = (
        "name", 
        "short_name"
    )


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = (
        "name", 
        "ral_code"
    )
    search_fields = (
        "name", 
        "ral_code"
    )


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )
    search_fields = (
        "name",
    )


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = (
        "name", 
        "country"
    )
    list_filter = (
        "country",
    )
    search_fields = (
        "name",
    )