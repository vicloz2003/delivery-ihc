from django.db import models
from django.conf import settings
import uuid


class Payment(models.Model):
    """Registro de pago con código QR"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Relación con pedido
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment'
    )
    
    # Información del pago
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        verbose_name="Estado"
    )
    
    # Código QR
    qr_code = models.TextField(
        blank=True,
        verbose_name="Código QR (Data URL)",
        help_text="Imagen del QR en formato base64"
    )
    
    # Referencia única del pago
    qr_reference = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Referencia QR"
    )
    
    # Información de transacción
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        null=True,
        verbose_name="ID de Transacción"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['qr_reference']),
            models.Index(fields=['transaction_id']),
        ]
    
    def __str__(self):
        return f"Pago {self.qr_reference} - {self.get_status_display()} - Bs. {self.amount}"
    
    @staticmethod
    def generate_qr_reference():
        """Generar referencia única para el QR"""
        return f"QR-{uuid.uuid4().hex[:12].upper()}"


class PaymentHistory(models.Model):
    """Historial de cambios en el pago"""
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='history'
    )
    
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_history'
        ordering = ['-created_at']
        verbose_name = 'Historial de Pago'
        verbose_name_plural = 'Historial de Pagos'
    
    def __str__(self):
        return f"{self.payment.qr_reference}: {self.old_status} → {self.new_status}"
