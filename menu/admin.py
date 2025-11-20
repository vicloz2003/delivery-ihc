from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'active_products_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description')
        }),
        ('Configuración', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'category', 
        'price', 
        'is_available', 
        'is_featured',
        'preparation_time', 
        'created_at'
    ]
    list_filter = ['category', 'is_available', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['category__name', 'name']
    list_editable = ['is_available', 'is_featured', 'price']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('category', 'name', 'description', 'image_url')
        }),
        ('Precio y Disponibilidad', {
            'fields': ('price', 'is_available', 'is_featured')
        }),
        ('Configuración', {
            'fields': ('preparation_time',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']