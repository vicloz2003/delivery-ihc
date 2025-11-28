# scripts/create_initial_data.py
import os
import django
from menu.models import Category, Product  # <-- AJUSTA ESTAS IMPORTACIONES A TUS MODELOS REALES

# Configura Django para poder usar los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def create_menu_data():
    print("Iniciando la carga de categorías y productos...")
    
    # 1. Eliminar datos existentes (para evitar duplicados)
    Product.objects.all().delete()
    Category.objects.all().delete()
    
    # 2. Creación de Categorías
    hamburguesa = Category.objects.create(name="Hamburguesas", description="Las mejores hamburguesas de la ciudad.")
    pollo = Category.objects.create(name="Pollo", description="Pollo frito y alitas.")
    pizza = Category.objects.create(name="Pizzas", description="Pizzas recién horneadas.")
    bebidas = Category.objects.create(name="Bebidas", description="Refrescos, jugos y más.")
    
    # 3. Creación de Productos (con URLs de imágenes de prueba)
    
    # Hamburguesas
    Product.objects.create(category=hamburguesa, name="Clásica Bacon", 
                           price=25.00, is_available=True, 
                           image="https://picsum.photos/id/1060/200/200")
    Product.objects.create(category=hamburguesa, name="Doble Queso", 
                           price=35.00, is_available=True, 
                           image="https://picsum.photos/id/350/200/200")
    
    # Pollo
    Product.objects.create(category=pollo, name="Alitas BBQ x 6", 
                           price=30.00, is_available=True, 
                           image="https://picsum.photos/id/104/200/200")

    # Bebidas
    Product.objects.create(category=bebidas, name="Refresco de Cola", 
                           price=8.00, is_available=True, 
                           image="https://picsum.photos/id/1080/200/200")
    
    print("Carga de datos de menú completada exitosamente.")

if __name__ == '__main__':
    create_menu_data()