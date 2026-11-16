# core/apps/catalog/models.py
from django.db import models


class Category(models.Model):
    """Древовидная категория."""
    
    workspace_id = models.UUIDField(
        'ID кабинета',
        db_index=True,
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительская категория',
    )
    name = models.CharField(
        'Название',
        max_length=150,
    )
    slug = models.SlugField(
        'Slig',
        max_length=150,
        blank=True,
    )
    path = models.CharField(
        'Путь',
        max_length=500, 
        db_index=True,
        blank=True,
    )
    depth = models.PositiveSmallIntegerField(
        'Глубина',
        default=0,
    )
    is_active = models.BooleanField(
        'Активна',
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Ктегории'
        ordering = [
            'path',
            'name',
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'workspace_id',
                    'parent',
                    'name',
                ],
                name='unique_category_name_per_parent',
                nulls_distinct=False,
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    'workspace_id',
                    'path',
                ]
            ),
        ]
                
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        
        # путь и глубина считаются от родителя
        if self.parent:
            self.depth = self.parent.depth +1
            parent_path = self.parent.path or ''
        else:
            self.depth = 0
            parent_path = ''
        super().save(*args, **kwargs)
        
        # после сохранения знаем pk — строим path
        new_path = f'{parent_path}{self.pk}/'
        if self.path != new_path:
            Category.objects.filter(pk=self.pk).update(path=new_path)
            self.path = new_path
            
    def descendants(self):
        """Все потомки (включая себя)"""
        
        return Category.objects.filter(
            workspace_id=self.workspace_id,
            path__startswith=self.path,
        )
        
        
class Product(models.Model):
    """Мастер-товар. Не продаётся напрямую — продаются варианты."""

    workspace_id = models.UUIDField(
        'ID кабинета', 
        db_index=True
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT,
        null=True, 
        blank=True, 
        related_name='products',
        verbose_name='Категория',
    )
    name = models.CharField(
        'Название', 
        max_length=200
    )
    image = models.ImageField(
        "Главное фото", upload_to="products/", blank=True, null=True,
    )
    description = models.TextField(
        'Описание', 
        blank=True
    )
    is_active = models.BooleanField(
        'Активен', 
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'workspace_id',
                    'name'
                ],
                name='unique_product_per_workspace',
            ),
        ]

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    """
    Вариант: цвет/размер. 
    Обязателен — даже для простого товара
    создаётся один вариант «Базовый».
    """

    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='variants',
    )
    name = models.CharField(
        'Название варианта', 
        max_length=150, 
        default='Базовый',
    )
    color = models.ForeignKey(
        'guide.Color', 
        on_delete=models.PROTECT,
        null=True, 
        blank=True, 
        verbose_name='Цвет',
    )
    image = models.ImageField(
        "Фото варианта", upload_to="variants/", blank=True, null=True,
    )
    vendor_code = models.CharField(
        'Артикул продавца', 
        max_length=100, 
        blank=True,
    )
    barcode = models.CharField(
        'Баркод', 
        max_length=100, 
        blank=True,
    )
    extra_cost = models.DecimalField(
        'Надбавка к себестоимости, ₽', 
        max_digits=12, 
        decimal_places=2, 
        default=0,
    )
    is_active = models.BooleanField(
        'Активен', 
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Вариант товара'
        verbose_name_plural = 'Варианты товара'
        ordering = [
            'product', 
            'name'
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'product', 
                    'name'
                ],
                name='unique_variant_name_per_product',
            ),
        ]

    def __str__(self):
        return f"{self.product} / {self.name}"
    
    
class PlatformListing(models.Model):
    """Карточка варианта на конкретной площадке."""

    class Status(models.TextChoices):
        DRAFT    = 'draft',     'Черновик'
        PENDING  = 'pending',   'На модерации'
        ACTIVE   = 'active',    'Активна'
        BLOCKED  = 'blocked',   'Заблокирована'
        ARCHIVED = 'archived',  'В архиве'

    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        related_name='listings',
    )
    marketplace = models.CharField(
        'Площадка', 
        max_length=20,
        choices=[
            ('wb', 'Wildberries'),
            ('ozon', 'Ozon'),
            ('yandex', 'Яндекс Маркет'),
            ('own', 'Свой сайт'),
            ('offline', 'Офлайн'),
        ],
    )
    platform_sku = models.CharField(
        'SKU площадки', 
        max_length=100, 
        blank=True
    )
    url = models.URLField(
        'Ссылка', 
        blank=True
    )
    status = models.CharField(
        'Статус', 
        max_length=20, 
        choices=Status.choices, 
        default=Status.DRAFT,
    )
    last_sync_at = models.DateTimeField(
        'Последняя синхронизация', 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Карточка на площадке'
        verbose_name_plural = 'Карточки на площадках'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'variant', 
                    'marketplace'
                ],
                name='unique_listing_per_variant_marketplace',
            ),
        ]

    def __str__(self):
        return f"{self.variant} @ {self.get_marketplace_display()}"