# menu/scripts/load_menu.py

from menu.models import Category, Product

def run():
    """
    Script para cargar datos iniciales de menú
    Solo crea/actualiza, no elimina productos con órdenes
    """
    
    print("Iniciando la carga de categorías y productos iniciales...")
    
    # ✅ NO eliminar todo - solo actualizar/crear
    # En lugar de: Product.objects.all().delete()
    # Hacemos: get_or_create
    
    # Definir categorías
    categories_data = [
        {"name": "Pizzas", "description": "Deliciosas pizzas artesanales"},
        {"name": "Hamburguesas", "description": "Hamburguesas gourmet"},
        {"name": "Bebidas", "description": "Bebidas frías y calientes"},
        {"name": "Postres", "description": "Dulces tentaciones"},
    ]
    
    print(f"Creando/actualizando {len(categories_data)} categorías...")
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data["name"],
            defaults={"description": cat_data["description"]}
        )
        if created:
            print(f"  ✅ Categoría creada: {category.name}")
        else:
            print(f"  ℹ️  Categoría ya existe: {category.name}")
    
    # Definir productos
    products_data = [
        # Pizzas
        {
            "name": "Pizza Margarita",
            "description": "Tomate, mozzarella, albahaca fresca",
            "price": 45.00,
            "category": "Pizzas",
            "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002",
        },
        {
            "name": "Pizza Pepperoni",
            "description": "Pepperoni, mozzarella, salsa de tomate",
            "price": 50.00,
            "category": "Pizzas",
            "image_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e",
        },
        {
            "name": "Pizza Vegetariana",
            "description": "Pimientos, champiñones, aceitunas, cebolla",
            "price": 48.00,
            "category": "Pizzas",
            "image_url": "https://images.unsplash.com/photo-1511689660979-10d2b1aada49",
        },
        
        # Hamburguesas
        {
            "name": "Hamburguesa Clásica",
            "description": "Carne de res, lechuga, tomate, cebolla, queso",
            "price": 38.00,
            "category": "Hamburguesas",
            "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd",
        },
        {
            "name": "Hamburguesa BBQ",
            "description": "Carne, tocino, queso cheddar, salsa BBQ",
            "price": 42.00,
            "category": "Hamburguesas",
            "image_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b",
        },
        
        # Bebidas
        {
            "name": "Coca Cola",
            "description": "Refresco 500ml",
            "price": 8.00,
            "category": "Bebidas",
            "image_url": "https://images.unsplash.com/photo-1554866585-cd94860890b7",
        },
        {
            "name": "Cerveza Artesanal",
            "description": "Cerveza local 330ml",
            "price": 22.00,
            "category": "Bebidas",
            "image_url": "https://images.unsplash.com/photo-1608270586620-248524c67de9",
        },
        {
            "name": "Jugo Natural",
            "description": "Jugo de frutas frescas 400ml",
            "price": 12.00,
            "category": "Bebidas",
            "image_url": "https://images.unsplash.com/photo-1600271886742-f049cd451bba",
        },
        
        # Postres
        {
            "name": "Cheesecake",
            "description": "Tarta de queso con frutos rojos",
            "price": 28.00,
            "category": "Postres",
            "image_url": "https://images.unsplash.com/photo-1533134242820-860c38a8e84e",
        },
        {
            "name": "Brownie con Helado",
            "description": "Brownie de chocolate con helado de vainilla",
            "price": 25.00,
            "category": "Postres",
            "image_url": "https://images.unsplash.com/photo-1607920591413-4ec007e70023",
        },
    ]
    
    print(f"Creando/actualizando {len(products_data)} productos...")
    
    for prod_data in products_data:
        category = Category.objects.get(name=prod_data["category"])
        
        product, created = Product.objects.update_or_create(
            name=prod_data["name"],
            defaults={
                "description": prod_data["description"],
                "price": prod_data["price"],
                "category": category,
                "image_url": prod_data["image_url"],
                "is_available": True,
            }
        )
        
        if created:
            print(f"  ✅ Producto creado: {product.name} - Bs.{product.price}")
        else:
            print(f"  🔄 Producto actualizado: {product.name} - Bs.{product.price}")
    
    print("\n✅ Carga de datos completada exitosamente")
    print(f"📊 Total categorías: {Category.objects.count()}")
    print(f"📊 Total productos: {Product.objects.count()}")