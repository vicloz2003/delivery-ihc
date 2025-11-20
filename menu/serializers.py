from rest_framework import serializers
from .models import Category, Product



class ProductSerializer(serializers.ModelSerializer):
    """Serializer básico para productos"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'category_name',
            'name',
            'description',
            'price',
            'image_url',
            'is_available',
            'is_featured',
            'preparation_time',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# -------------------------------------------------------
# Serializer: Product (Para bot de Telegram - vista simplificada)
# -------------------------------------------------------
class ProductBotSerializer(serializers.ModelSerializer):
    """Serializer simplificado para el bot de Telegram"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'category_name',
            'name',
            'description',
            'price',
            'image_url',
            'preparation_time',
        ]



class CategorySerializer(serializers.ModelSerializer):
    """Serializer básico para categorías"""
    
    active_products_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'active_products_count',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']



class CategoryWithProductsSerializer(serializers.ModelSerializer):
    """Serializer de categoría con todos sus productos"""
    
    products = ProductSerializer(many=True, read_only=True)
    active_products_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'active_products_count',
            'products',
        ]


# -------------------------------------------------------
# Serializer: Category con productos (para bot de Telegram)
# -------------------------------------------------------
class CategoryWithProductsBotSerializer(serializers.ModelSerializer):
    """Serializer simplificado para el bot"""
    
    products = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'products',
        ]
    
    def get_products(self, obj):
        """Solo productos disponibles"""
        products = obj.products.filter(is_available=True)
        return ProductBotSerializer(products, many=True).data



class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar productos"""
    
    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'description',
            'price',
            'image_url',
            'is_available',
            'is_featured',
            'preparation_time',
        ]
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        return value
    
    def validate_preparation_time(self, value):
        if value < 1:
            raise serializers.ValidationError("El tiempo de preparación debe ser al menos 1 minuto")
        return value



class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar categorías"""
    
    class Meta:
        model = Category
        fields = [
            'name',
            'description',
            'is_active',
        ]
    
    def validate_name(self, value):
        # Verificar unicidad al crear
        instance = self.instance
        if Category.objects.filter(name__iexact=value).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError("Ya existe una categoría con este nombre")
        return value