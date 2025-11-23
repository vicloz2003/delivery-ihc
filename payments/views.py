from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import qrcode
from io import BytesIO
import base64
from django.utils import timezone

from .models import Payment, PaymentHistory
from .serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentCreateSerializer,
)
from orders.models import Order


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de pagos con código QR (simulado)
    
    - create: Crear pago y generar QR
    - confirm: Confirmar pago (cambios automáticos)
    """
    
    queryset = Payment.objects.select_related('order').prefetch_related('history')
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        if self.action == 'create_qr':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        """Filtrar pagos según permisos"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_staff:
            return queryset
        
        # Cliente solo ve sus propios pagos
        return queryset.filter(order__client=user)
    
    @action(detail=False, methods=['post'])
    def create_qr(self, request):
        """
        Endpoint: POST /api/payments/create_qr/
        Crear pago y generar código QR
        
        Body: {"order_id": 1}
        
        Response:
        {
            "id": 1,
            "order": 1,
            "amount": 100.00,
            "qr_code": "data:image/png;base64,...",
            "qr_reference": "QR-ABC123DEF456",
            "status": "pending"
        }
        """
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        
        try:
            order = Order.objects.get(id=order_id, client=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validar que el pedido esté en estado "pending"
        if order.status != 'pending':
            return Response(
                {'error': f'El pedido ya está en estado {order.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que no tenga pago
        if hasattr(order, 'payment'):
            return Response(
                {'error': 'Este pedido ya tiene un pago'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear pago
        qr_reference = Payment.generate_qr_reference()
        payment = Payment.objects.create(
            order=order,
            amount=order.total,
            qr_reference=qr_reference,
            status='pending'
        )
        
        # Generar código QR (simulado)
        payment.qr_code = self._generate_qr_code(payment)
        payment.save()
        
        # Registrar en historial
        PaymentHistory.objects.create(
            payment=payment,
            old_status='',
            new_status='pending',
            notes='Pago iniciado - QR generado'
        )
        
        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Endpoint: POST /api/payments/{id}/confirm/
        Confirmar pago (simula escaneo y pago)
        
        Body: {} (vacío)
        
        Cambios automáticos:
        - Payment status: pending → completed
        - Order status: pending → confirmed
        """
        payment = self.get_object()
        
        # Validar que sea del cliente
        if payment.order.client != request.user:
            return Response(
                {'error': 'No tienes permisos para este pago'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validar estado
        if payment.status != 'pending':
            return Response(
                {'error': f'El pago ya está {payment.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ========== CAMBIOS AUTOMÁTICOS ==========
        
        # 1. Actualizar pago
        old_status = payment.status
        payment.status = 'completed'
        payment.confirmed_at = timezone.now()
        payment.save()
        
        # 2. Registrar en historial
        PaymentHistory.objects.create(
            payment=payment,
            old_status=old_status,
            new_status='completed',
            notes='Pago simulado - QR escaneado'
        )
        
        # 3. Actualizar pedido AUTOMÁTICAMENTE
        order = payment.order
        order.status = 'confirmed'
        order.confirmed_at = timezone.now()
        order.save()
        
        # 4. Registrar cambio en historial del pedido
        from orders.models import OrderStatusHistory
        OrderStatusHistory.objects.create(
            order=order,
            status='confirmed',
            changed_by=request.user,
            notes='Confirmado por pago'
        )
        
        return Response(
            {
                'message': '✅ Pago confirmado - Pedido confirmado',
                'payment': PaymentSerializer(payment).data,
                'order_status': order.get_status_display()
            },
            status=status.HTTP_200_OK
        )
    
    @staticmethod
    def _generate_qr_code(payment):
        """Generar QR visual (solo para MVP)"""
        try:
            # Datos del QR
            qr_data = f"PAGO|{payment.qr_reference}|Bs.{payment.amount}|{payment.order.order_number}"
            
            # Crear QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Convertir a imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            print(f"Error generando QR: {e}")
            return ""
