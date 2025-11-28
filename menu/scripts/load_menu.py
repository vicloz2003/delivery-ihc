# menu/scripts/load_menu.py
from .models import Category, Product 
import decimal

def run():
    """
    Función de carga de datos iniciales. 
    Ejecutada por: python manage.py runscript load_menu
    """
    print("Iniciando la carga de categorías y productos iniciales...")
    
    # --- 1. Limpieza de Datos (Importante para evitar duplicados en cada despliegue) ---
    Product.objects.all().delete()
    Category.objects.all().delete()
    print("Datos de categorías y productos existentes eliminados.")
    
    # --- 2. Creación de Categorías ---
    try:
        entradas = Category.objects.create(name="Entradas", description="Complementos y acompañamientos.")
        hamburguesa = Category.objects.create(name="Hamburguesas", description="Nuestras especialidades gourmet.")
        bebidas = Category.objects.create(name="Bebidas", description="Refrescos, jugos naturales y cervezas.")
        postres = Category.objects.create(name="Postres", description="El final perfecto para tu pedido.")
        print(f"Creadas {Category.objects.count()} categorías.")
    except Exception as e:
        print(f"Error al crear categorías: {e}")
        return # Detiene la ejecución si falla la categoría

    # --- 3. Creación de Productos ---
    
    # Hamburguesas
    Product.objects.create(category=hamburguesa, name="Cheese Bacon Deluxe", 
                           price=decimal.Decimal("38.50"), is_available=True, is_featured=True,
                           image_url="https://picsum.photos/id/350/200/200", 
                           preparation_time=20, description="Doble carne, queso cheddar y tocino crujiente.")
                           
    Product.objects.create(category=hamburguesa, name="Clásica Simple", 
                           price=decimal.Decimal("25.00"), is_available=True, 
                           image_url="https://picsum.photos/id/1060/200/200", 
                           preparation_time=15, description="Carne de res, lechuga, tomate y salsa de la casa.")
    
    # Entradas
    Product.objects.create(category=entradas, name="Papas Fritas Grandes", 
                           price=decimal.Decimal("15.00"), is_available=True, 
                           image_url="https://picsum.photos/id/1004/200/200", 
                           preparation_time=10, description="Papas fritas al estilo rústico.")
                           
    Product.objects.create(category=entradas, name="Aros de Cebolla", 
                           price=decimal.Decimal("18.00"), is_available=True, 
                           image_url="https://picsum.photos/id/111/200/200", 
                           preparation_time=12, description="Cebollas fritas y crujientes.")
    
    # Bebidas
    Product.objects.create(category=bebidas, name="Limonada Natural", 
                           price=decimal.Decimal("10.00"), is_available=True, 
                           image_url="https://picsum.photos/id/1080/200/200",
                           preparation_time=5, description="Refrescante limonada recién hecha.")
                           
    Product.objects.create(category=bebidas, name="Cerveza Artesanal", 
                           price=decimal.Decimal("22.00"), is_available=True, 
                           image_url="https://picsum.photos/id/1057/200/200",
                           preparation_time=5, description="Cerveza local, estilo IPA.")

    # Postres
    Product.objects.create(category=postres, name="Brownie con Helado", 
                           price=decimal.Decimal("20.00"), is_available=True, 
                           image_url="https://picsum.photos/id/225/200/200", 
                           preparation_time=7, description="Brownie de chocolate caliente con helado de vainilla.")
                           
    print(f"Carga de datos de menú completada exitosamente. Total de productos: {Product.objects.count()}")