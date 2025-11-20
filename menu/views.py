from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Product
from .serializers import (
    CategorySerializer,
    CategoryWithProductsSerializer,
    CategoryWithProductsBotSerializer,
    CategoryCreateUpdateSerializer,
    ProductSerializer,
    ProductBotSerializer,
    ProductCreateUpdateSerializer,
)


# -------------------------------------------------------
# ViewSet: Category
# -------------------------------------------------------
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de categorías del menú
    
    - list: Ver todas las categorías (público)
    - retrieve: Ver una categoría específica (público)
    - create: Crear categoría (admin)
    - update: Actualizar categoría (admin)
    - destroy: Eliminar categoría (admin)
    - with_products: Ver categorías con sus productos (público)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """
        - GET (list, retrieve): Público
        - POST, PUT, PATCH, DELETE: Solo admin
        """
        if self.action in ['list', 'retrieve', 'with_products', 'bot_menu']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateUpdateSerializer
        if self.action == 'with_products':
            return CategoryWithProductsSerializer
        if self.action == 'bot_menu':
            return CategoryWithProductsBotSerializer
        return CategorySerializer
    
    def get_queryset(self):
        """Filtrar solo categorías activas para clientes"""
        queryset = super().get_queryset()
        
        # Si el usuario es admin, mostrar todas
        if self.request.user.is_staff:
            return queryset
        
        # Para otros usuarios, solo categorías activas
        return queryset.filter(is_active=True)
    
    @action(detail=False, methods=['get'], url_path='with-products')
    def with_products(self, request):
        """
        Endpoint: GET /api/menu/categories/with-products/
        Devuelve todas las categorías activas con sus productos disponibles
        """
        categories = self.get_queryset().filter(is_active=True).prefetch_related('products')
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='bot-menu')
    def bot_menu(self, request):
        """
        Endpoint: GET /api/menu/categories/bot-menu/
        Menú simplificado para el bot de Telegram
        Solo categorías y productos disponibles
        """
        categories = Category.objects.filter(
            is_active=True
        ).prefetch_related(
            'products'
        )
        
        serializer = self.get_serializer(categories, many=True)
        return Response({
            'categories': serializer.data,
            'total_categories': categories.count(),
        })


# -------------------------------------------------------
# ViewSet: Product
# -------------------------------------------------------
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de productos del menú
    
    - list: Ver todos los productos (público)
    - retrieve: Ver un producto específico (público)
    - create: Crear producto (admin)
    - update: Actualizar producto (admin)
    - destroy: Eliminar producto (admin)
    - featured: Ver productos destacados (público)
    - by_category: Ver productos de una categoría (público)
    """
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['category__name', 'name']
    
    def get_permissions(self):
        """
        - GET (list, retrieve): Público
        - POST, PUT, PATCH, DELETE: Solo admin
        """
        if self.action in ['list', 'retrieve', 'featured', 'by_category', 'available']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        if self.action in ['available', 'by_category']:
            return ProductBotSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Filtrar solo productos disponibles para clientes"""
        queryset = super().get_queryset()
        
        # Si el usuario es admin, mostrar todos
        if self.request.user.is_staff:
            return queryset
        
        # Para otros usuarios, solo productos disponibles
        return queryset.filter(is_available=True, category__is_active=True)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Endpoint: GET /api/menu/products/featured/
        Devuelve productos destacados y disponibles
        """
        products = self.get_queryset().filter(is_featured=True, is_available=True)[:10]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='category/(?P<category_id>[^/.]+)')
    def by_category(self, request, category_id=None):
        """
        Endpoint: GET /api/menu/products/category/{category_id}/
        Devuelve productos de una categoría específica
        """
        products = self.get_queryset().filter(
            category_id=category_id,
            is_available=True
        )
        serializer = self.get_serializer(products, many=True)
        return Response({
            'category_id': category_id,
            'products': serializer.data,
            'total': products.count(),
        })
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Endpoint: GET /api/menu/products/available/
        Todos los productos disponibles (para el bot)
        """
        products = self.get_queryset().filter(is_available=True)
        serializer = self.get_serializer(products, many=True)
        return Response({
            'products': serializer.data,
            'total': products.count(),
        })
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """
        Endpoint: POST /api/menu/products/{id}/toggle_availability/
        Cambiar disponibilidad de un producto (solo admin)
        """
        product = self.get_object()
        product.is_available = not product.is_available
        product.save()
        
        serializer = self.get_serializer(product)
        return Response({
            'message': f"Producto {'activado' if product.is_available else 'desactivado'}",
            'product': serializer.data
        })