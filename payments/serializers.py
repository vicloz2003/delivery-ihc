from rest_framework import serializers
from .models import Payment, PaymentHistory


class PaymentHistorySerializer(serializers.ModelSerializer):
    """Historial de cambios"""
    
    class Meta:
        model = PaymentHistory
        fields = ['id', 'old_status', 'new_status', 'notes', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagos"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    history = PaymentHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'order',
            'order_number',
            'amount',
            'status',
            'status_display',
            'qr_code',
            'qr_reference',
            'created_at',
            'confirmed_at',
            'history',
        ]
        read_only_fields = ['id', 'qr_code', 'qr_reference', 'created_at']


class PaymentListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'order_number', 'amount', 'status', 'status_display', 'created_at']


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer para crear pago"""
    
    order_id = serializers.IntegerField()
    
    def validate_order_id(self, value):
        """Validar que el pedido existe"""
        from orders.models import Order
        try:
            Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Pedido no existe")
        return value
