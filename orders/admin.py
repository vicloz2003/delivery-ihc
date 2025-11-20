from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['unit_price', 'subtotal']
    fields = ['product', 'quantity', 'unit_price', 'subtotal', 'notes']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'changed_by', 'created_at']
    fields = ['status', 'changed_by', 'notes', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'client',
        'status',
        'total',
        'driver',
        'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'client__email', 'delivery_address']
    readonly_fields = [
        'order_number',
        'subtotal',
        'total',
        'created_at',
        'confirmed_at',
        'assigned_at',
        'delivered_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('order_number', 'client', 'status')
        }),
        ('Entrega', {
            'fields': (
                'delivery_address',
                'delivery_latitude',
                'delivery_longitude',
                'delivery_reference',
                'driver',
            )
        }),
        ('Montos', {
            'fields': ('subtotal', 'delivery_fee', 'total')
        }),
        ('Observaciones', {
            'fields': ('notes',)
        }),
        ('Tiempos', {
            'fields': (
                'created_at',
                'confirmed_at',
                'assigned_at',
                'delivered_at',
                'updated_at',
            )
        }),
    )
    
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    def save_model(self, request, obj, form, change):
        """Registrar cambios de estado en el historial"""
        if change:  # Si es una actualización
            old_obj = Order.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                # Se cambió el estado, registrar en historial
                super().save_model(request, obj, form, change)
                OrderStatusHistory.objects.create(
                    order=obj,
                    status=obj.status,
                    changed_by=request.user,
                    notes=f'Estado actualizado desde admin'
                )
                return
        
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['order__order_number', 'product__name']
    readonly_fields = ['unit_price', 'subtotal']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'changed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number']
    readonly_fields = ['created_at']