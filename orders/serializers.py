# orders/serializers.py

from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from .models import Order, OrderItem, OrderStatusHistory
from menu.models import Product
from menu.serializers import ProductSerializer
from core.serializers import UserSerializer


# -------------------------------------------------------
# Serializer: OrderItem (para lectura)
# -------------------------------------------------------
class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer para mostrar items del pedido"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.CharField(source='product.image_url', read_only=True)
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_image',
            'product_details',
            'quantity',
            'unit_price',
            'subtotal',
            'notes',
        ]
        read_only_fields = ['id', 'unit_price', 'subtotal']


# -------------------------------------------------------
# Serializer: OrderItem (para crear pedido)
# -------------------------------------------------------
class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer para crear items al hacer un pedido"""
    
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    
    def validate_product_id(self, value):
        """Validar que el producto exista y esté disponible"""
        print(f"[DEBUG-PRODUCT-ID] Validando product_id: {value}")
        
        try:
            product = Product.objects.get(id=value)
            print(f"[DEBUG-PRODUCT-ID] ✓ Producto encontrado: {product.name}")
            
            if not product.is_available:
                print(f"[DEBUG-PRODUCT-ID] ✗ Producto NO disponible")
                raise serializers.ValidationError(
                    f"El producto '{product.name}' no está disponible"
                )
            
            print(f"[DEBUG-PRODUCT-ID] ✓ Validación OK")
            return value
            
        except Product.DoesNotExist:
            print(f"[DEBUG-PRODUCT-ID] ✗ Producto NO EXISTE con id={value}")
            raise serializers.ValidationError(
                f"El producto con ID {value} no existe"
            )


# -------------------------------------------------------
# Serializer: Order (para lectura completa)
# -------------------------------------------------------
class OrderSerializer(serializers.ModelSerializer):
    """Serializer completo para mostrar pedidos"""
    
    client_details = UserSerializer(source='client', read_only=True)
    driver_details = UserSerializer(source='driver', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    estimated_preparation_time = serializers.IntegerField(read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'client',
            'client_details',
            'driver',
            'driver_details',
            'status',
            'status_display',
            'delivery_latitude',
            'delivery_longitude',
            'delivery_address',
            'delivery_reference',
            'subtotal',
            'delivery_fee',
            'total',
            'notes',
            'items',
            'estimated_preparation_time',
            'total_items',
            'created_at',
            'confirmed_at',
            'assigned_at',
            'delivered_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'order_number',
            'subtotal',
            'total',
            'created_at',
            'updated_at',
        ]


# -------------------------------------------------------
# Serializer: Order (vista simplificada para listas)
# -------------------------------------------------------
class OrderListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar pedidos"""
    
    client_email = serializers.EmailField(source='client.email', read_only=True)
    driver_email = serializers.EmailField(source='driver.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'client_email',
            'driver_email',
            'status',
            'status_display',
            'total',
            'total_items',
            'created_at',
        ]


# -------------------------------------------------------
# Serializer: Crear Order (desde Mini App)
# -------------------------------------------------------
class OrderCreateSerializer(serializers.Serializer):
    """Serializer para crear un pedido desde la Mini App"""

    # Ubicación (obligatoria, viene de Telegram)
    delivery_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    delivery_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    delivery_reference = serializers.CharField(required=False, allow_blank=True, default='')

    # Costo de envío (calculado por backend según distancia)
    delivery_fee = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('10.00'),
        required=False
    )

    # Observaciones generales del pedido
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    # Items del pedido
    items = OrderItemCreateSerializer(many=True)

    def validate_items(self, value):
        """Validar que haya al menos un item"""
        print(f"[DEBUG-VALIDATE-ITEMS] Validando {len(value)} items")
        
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un producto")
        
        return value

    def validate(self, attrs):
        """Validaciones generales - validar cada producto individualmente"""
        print(f"[DEBUG-VALIDATE] Iniciando validación general")
        print(f"[DEBUG-VALIDATE] Datos recibidos: {attrs}")
        
        items_data = attrs.get('items', [])
        print(f"[DEBUG-VALIDATE] Total items: {len(items_data)}")
        
        # Validar que todos los productos existan y estén disponibles
        for idx, item in enumerate(items_data):
            product_id = item.get('product_id')
            print(f"[DEBUG-VALIDATE] Item {idx+1}: product_id={product_id}")
            
            try:
                product = Product.objects.get(id=product_id)
                print(f"[DEBUG-VALIDATE] Producto: {product.name}, disponible={product.is_available}")
                
                if not product.is_available:
                    raise serializers.ValidationError(
                        f"El producto '{product.name}' no está disponible"
                    )
                    
            except Product.DoesNotExist:
                print(f"[DEBUG-VALIDATE] ERROR: Producto {product_id} no existe")
                raise serializers.ValidationError(
                    f"El producto con ID {product_id} no existe"
                )
        
        print(f"[DEBUG-VALIDATE] ✓ Validación completada")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Crear el pedido con sus items"""
        print("="*60)
        print(f"[DEBUG-CREATE] 🚀 INICIANDO CREACIÓN DE ORDEN")
        print("="*60)
        
        try:
            # Obtener usuario del contexto
            request = self.context.get('request')
            if not request or not request.user:
                raise serializers.ValidationError("Usuario no autenticado")
            
            user = request.user
            print(f"[DEBUG-CREATE] Usuario: {user.id} - {user.email}")
            print(f"[DEBUG-CREATE] Role: {user.role}")
            
            # Extraer items
            items_data = validated_data.pop('items')
            print(f"[DEBUG-CREATE] Items a procesar: {len(items_data)}")
            
            # Calcular subtotal
            subtotal = Decimal('0.00')
            items_to_create = []
            
            for idx, item_data in enumerate(items_data):
                product_id = item_data['product_id']
                quantity = item_data['quantity']
                
                print(f"[DEBUG-CREATE] Procesando item {idx+1}:")
                print(f"  - product_id: {product_id}")
                print(f"  - quantity: {quantity}")
                
                try:
                    product = Product.objects.get(id=product_id)
                    unit_price = product.price
                    item_subtotal = unit_price * quantity
                    subtotal += item_subtotal
                    
                    print(f"  - product: {product.name}")
                    print(f"  - unit_price: {unit_price}")
                    print(f"  - item_subtotal: {item_subtotal}")
                    
                    items_to_create.append({
                        'product': product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'subtotal': item_subtotal,
                        'notes': item_data.get('notes', ''),
                    })
                    
                except Product.DoesNotExist:
                    print(f"  ❌ ERROR: Producto {product_id} no existe")
                    raise serializers.ValidationError(
                        f"Producto con ID {product_id} no encontrado"
                    )
            
            print(f"[DEBUG-CREATE] Subtotal calculado: {subtotal}")
            
            # Obtener delivery_fee
            delivery_fee = validated_data.get('delivery_fee', Decimal('10.00'))
            print(f"[DEBUG-CREATE] Delivery fee: {delivery_fee}")
            
            # Dirección (por implementar con Google Maps)
            delivery_address = ""
            
            # Crear el pedido
            print(f"[DEBUG-CREATE] 📦 Creando Order...")
            order = Order.objects.create(
                client=user,
                delivery_latitude=validated_data['delivery_latitude'],
                delivery_longitude=validated_data['delivery_longitude'],
                delivery_address=delivery_address,
                delivery_reference=validated_data.get('delivery_reference', ''),
                delivery_fee=delivery_fee,
                notes=validated_data.get('notes', ''),
                subtotal=subtotal,
            )
            print(f"[DEBUG-CREATE] ✅ Order creada: {order.order_number} (ID: {order.id})")
            
            # Crear los items
            print(f"[DEBUG-CREATE] 📝 Creando {len(items_to_create)} OrderItems...")
            for item_data in items_to_create:
                OrderItem.objects.create(order=order, **item_data)
            print(f"[DEBUG-CREATE] ✅ OrderItems creados")
            
            # Crear registro en historial
            print(f"[DEBUG-CREATE] 📋 Creando OrderStatusHistory...")
            OrderStatusHistory.objects.create(
                order=order,
                status='pending',
                changed_by=user,
                notes='Pedido creado desde Mini App'
            )
            print(f"[DEBUG-CREATE] ✅ OrderStatusHistory creado")
            
            print("="*60)
            print(f"[DEBUG-CREATE] 🎉 ORDEN CREADA EXITOSAMENTE")
            print(f"[DEBUG-CREATE] Order Number: {order.order_number}")
            print(f"[DEBUG-CREATE] Total: {order.total}")
            print("="*60)
            
            return order
            
        except Exception as e:
            print("="*60)
            print(f"[DEBUG-CREATE] ❌ ERROR CRÍTICO")
            print(f"[DEBUG-CREATE] Tipo: {type(e).__name__}")
            print(f"[DEBUG-CREATE] Mensaje: {str(e)}")
            print("="*60)
            
            import traceback
            traceback.print_exc()
            
            # Re-lanzar la excepción para que DRF la maneje
            raise


# -------------------------------------------------------
# Serializer: Actualizar estado del pedido
# -------------------------------------------------------
class OrderUpdateStatusSerializer(serializers.Serializer):
    """Serializer para cambiar el estado de un pedido"""
    
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    
    def validate_status(self, value):
        """Validar transiciones de estado permitidas"""
        order = self.context.get('order')
        current_status = order.status
        
        # Definir transiciones válidas
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['preparing', 'cancelled'],
            'preparing': ['ready', 'cancelled'],
            'ready': ['assigned', 'cancelled'],
            'assigned': ['in_transit', 'cancelled'],
            'in_transit': ['delivered', 'cancelled'],
            'delivered': [],
            'cancelled': [],
        }
        
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"No se puede cambiar de '{current_status}' a '{value}'"
            )
        
        return value
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Actualizar el estado del pedido"""
        new_status = validated_data['status']
        notes = validated_data.get('notes', '')
        user = self.context['request'].user
        
        # Actualizar el pedido
        instance.status = new_status
        
        # Actualizar timestamps según el estado
        if new_status == 'confirmed':
            from django.utils import timezone
            instance.confirmed_at = timezone.now()
        elif new_status == 'assigned':
            from django.utils import timezone
            instance.assigned_at = timezone.now()
        elif new_status == 'delivered':
            from django.utils import timezone
            instance.delivered_at = timezone.now()
        
        instance.save()
        
        # Registrar en historial
        OrderStatusHistory.objects.create(
            order=instance,
            status=new_status,
            changed_by=user,
            notes=notes
        )
        
        return instance