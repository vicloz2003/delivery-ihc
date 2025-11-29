from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Order, OrderStatusHistory
from .serializers import (
    OrderSerializer,
    OrderListSerializer,
    OrderCreateSerializer,
    OrderUpdateStatusSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de pedidos
    
    ENDPOINTS PRINCIPALES (según documento):
    - list: Ver pedidos (cliente ve solo suyos, conductor ve asignados)
    - retrieve: Ver detalle de un pedido
    - create: Crear nuevo pedido desde bot de Telegram
    - update_status: Cambiar estado del pedido
    - my_orders: Mis pedidos (para bot)
    - my_deliveries: Mis entregas (para app conductor)
    - cancel: Cancelar pedido
    """
    
    queryset = Order.objects.select_related('client', 'driver').prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['order_number']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action == 'update_status':
            return OrderUpdateStatusSerializer
        return OrderSerializer
    
    def get_queryset(self):
        """
        - Admin: Ve todos los pedidos
        - Cliente: Solo sus pedidos
        - Conductor: Solo pedidos asignados a él
        """
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_staff:
            return queryset
        
        if user.role == 'DRIVER':
            return queryset.filter(driver=user)
        
        # Cliente ve solo sus pedidos
        return queryset.filter(client=user)
    
    def perform_create(self, serializer):
                        # El usuario ya viene autenticado por el middleware
                        # Solo aseguramos que sea CUSTOMER
                        print(f"[DEBUG-VIEW] perform_create llamado")
                        print(f"[DEBUG-VIEW] Usuario: {self.request.user.id}, Role: {self.request.user.role}")
                        if self.request.user.role != 'CUSTOMER':
                            print(f"[DEBUG-VIEW] ❌ Usuario no es CUSTOMER")
                            from rest_framework.exceptions import PermissionDenied
                            raise PermissionDenied("Solo clientes pueden crear pedidos")
                        print(f"[DEBUG-VIEW] ✓ Usuario es CUSTOMER, llamando a serializer.save()")
                        serializer.save()    @action(detail=False, methods=['get'], url_path='my-orders')
    def my_orders(self, request):
        """
        Endpoint: GET /api/orders/my-orders/
        Ver todos mis pedidos como cliente (para el bot)
        """
        orders = self.get_queryset().filter(client=request.user)
        
        # Filtro opcional por estado
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        serializer = OrderListSerializer(orders, many=True)
        return Response({
            'count': orders.count(),
            'orders': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='my-deliveries')
    def my_deliveries(self, request):
        """
        Endpoint: GET /api/orders/my-deliveries/
        Ver mis entregas asignadas como conductor (para app móvil)
        """
        if request.user.role != 'DRIVER':
            return Response(
                {'error': 'Solo conductores pueden acceder a este endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Solo pedidos asignados y en estados activos
        orders = self.get_queryset().filter(
            driver=request.user,
            status__in=['assigned', 'in_transit']
        )
        
        serializer = OrderSerializer(orders, many=True)
        return Response({
            'count': orders.count(),
            'orders': serializer.data
        })
    
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Endpoint: POST /api/orders/{id}/update-status/
        Actualizar el estado de un pedido
        
        Usado por:
        - Conductor: para marcar "in_transit" o "delivered"
        - Admin: para confirmar pedido
        
        Body: {"status": "in_transit"}
        """
        order = self.get_object()
        
        serializer = OrderUpdateStatusSerializer(
            order,
            data=request.data,
            context={'request': request, 'order': order}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Endpoint: POST /api/orders/{id}/cancel/
        Cancelar un pedido (cliente o conductor)
        Body: {"reason": "Cliente canceló"}
        """
        order = self.get_object()
        
        # Solo el cliente, conductor asignado o admin pueden cancelar
        can_cancel = (
            order.client == request.user or
            order.driver == request.user or
            request.user.is_staff
        )
        
        if not can_cancel:
            return Response(
                {'error': 'No tiene permisos para cancelar este pedido'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # No se puede cancelar si ya está entregado
        if order.status in ['delivered', 'cancelled']:
            return Response(
                {'error': f'No se puede cancelar un pedido {order.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', 'Sin razón especificada')
        
        order.status = 'cancelled'
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            changed_by=request.user,
            notes=f'Cancelado: {reason}'
        )
        
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK
        )