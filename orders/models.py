from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
from datetime import datetime


class Order(models.Model):
    """Pedido principal"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('preparing', 'En Preparación'),
        ('ready', 'Listo para Entrega'),
        ('assigned', 'Conductor Asignado'),
        ('in_transit', 'En Camino'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Número de orden único
    order_number = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Cliente
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        limit_choices_to={'role': 'CUSTOMER'}
    )
    
    # Estado del pedido
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    
    # Ubicación de entrega (desde Telegram)
    delivery_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Latitud"
    )
    delivery_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Longitud"
    )
    delivery_address = models.TextField(
        blank=True,
        verbose_name="Dirección",
        help_text="Se obtiene automáticamente de las coordenadas"
    )
    delivery_reference = models.TextField(
        blank=True,
        verbose_name="Referencia",
        help_text="Ej: Casa azul, portón negro"
    )
    
    # Montos
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Subtotal"
    )
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10.00,
        validators=[MinValueValidator(0)],
        verbose_name="Costo de envío"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Total"
    )
    
    # Observaciones del cliente
    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
        help_text="Observaciones generales del pedido"
    )
    
    # Conductor asignado (automáticamente)
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries',
        limit_choices_to={'role': 'DRIVER'}
    )
    
    # Tiempos
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['client', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['driver', 'status']),
        ]
    
    def __str__(self):
        return f"{self.order_number} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Generar número de orden si no existe
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        # Calcular total automáticamente
        if self.subtotal is not None:
            self.total = self.subtotal + self.delivery_fee
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_order_number():
        """Genera un número de orden único: ORD-20250117-XXXX"""
        today = datetime.now().strftime('%Y%m%d')
        random_part = str(uuid.uuid4().hex)[:4].upper()
        return f"ORD-{today}-{random_part}"
    
    @property
    def estimated_preparation_time(self):
        """Tiempo estimado de preparación basado en los items"""
        max_time = 0
        for item in self.items.all():
            if item.product.preparation_time > max_time:
                max_time = item.product.preparation_time
        return max_time
    
    @property
    def total_items(self):
        """Total de items en el pedido"""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0


class OrderItem(models.Model):
    """Items individuales del pedido"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'menu.Product',
        on_delete=models.PROTECT,
        verbose_name="Producto"
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio unitario"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Subtotal"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
        help_text="Ej: Sin cebolla, extra picante"
    )
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        if self.unit_price and self.quantity:
            self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Historial de cambios de estado del pedido"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_status_history'
        ordering = ['-created_at']
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status} - {self.created_at}"