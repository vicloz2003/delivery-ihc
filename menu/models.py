from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    """Categorías del menú (Entradas, Platos Fuertes, Bebidas, Postres)"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        ordering = ['name']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.name
    
    @property
    def active_products_count(self):
        """Cantidad de productos activos en esta categoría"""
        return self.products.filter(is_available=True).count()


class Product(models.Model):
    """Productos del menú del restaurante"""
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Categoría"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio"
    )
    image_url = models.URLField(
        blank=True,
        max_length=500,
        help_text="URL de la imagen del producto",
        verbose_name="Imagen URL"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Desmarcar si el producto no está disponible temporalmente",
        verbose_name="Disponible"
    )
    preparation_time = models.IntegerField(
        default=15,
        validators=[MinValueValidator(1)],
        help_text="Tiempo de preparación en minutos",
        verbose_name="Tiempo de preparación"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Marcar para destacar en el menú",
        verbose_name="Destacado"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['category__name', 'name']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['category', 'is_available']),
            models.Index(fields=['is_featured', 'is_available']),
        ]

    def __str__(self):
        status = "✓" if self.is_available else "✗"
        return f"{status} {self.name} - Bs. {self.price}"