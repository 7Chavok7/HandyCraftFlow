# core/apps/guide/models.py
from django.db import models


class Unit(models.Model):
    """Общий класс. Единицы измерения"""
    name = models.CharField(
        "Наименование",
        max_length=25,
        unique=True,
    )
    short_name = models.CharField(
        "Сокращение",
        max_length=10,
        unique=True,
    )
    
    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'
        
    def __str__(self):
        return self.short_name


class Color(models.Model):
    """Общий класс. Цвет"""
    name = models.CharField(
        'Название цвета',
        max_length=150,
        unique=True,
    )
    ral_code = models.CharField(
        "Код по RAL",
        max_length=10,
        unique=True,
        blank=True,
        null=True,
    )
    RGB_code = models.CharField(
        "Код по RGB",
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )
    CMYK_code = models.CharField(
        "Код по CMYK",
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )
    
    class Meta:
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'
        
    def __str__(self):
        if self.ral_code:
            return f"{self.name}({self.ral_code})"
        return self.name
    
    
class Country(models.Model):   
    """Общий класс. Страна."""
    name = models.CharField(
        "Страна",
        max_length=150,
        unique=True,
    )
    
    class Meta:
        verbose_name = 'Страна',
        verbose_name_plural = 'Страны'
        
    def __str__(self):
        return self.name
    
    
class Manufacturer(models.Model):
    """Общий класс. Произыодитель."""
    name = models.CharField(
        'Наименование производителя',
        max_length=150,
        unique=True,
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Страна производства',
    )
    
    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
        
    def __str__(self):
        if self.country:
            return f"{self.name} ({self.country})"
        return self.name
    