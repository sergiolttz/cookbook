from django.core.management.base import BaseCommand
from recipes.models import Recipe, Ingredient, RecipeIngredient, Step, Tag
from django.contrib.auth.models import User
from datetime import timedelta

class Command(BaseCommand):
    help = 'Importa un conjunto de recetas populares automáticamente'

    def handle(self, *args, **options):
        try:
            autor = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Usuario 'admin' no encontrado. Crea uno o cambia el nombre en el script."))
            return

        recetas = [
        {
            "title": "Pizza Margarita",
            "description": "Pizza clásica italiana con tomate, mozzarella y albahaca.",
            "time_required": timedelta(minutes=45),
            "servings": 2,
            "ingredients": [
                ("Masa para pizza", 1, "u"),
                ("Tomate triturado", 150, "ml"),
                ("Mozzarella", 100, "gr"),
                ("Hojas de albahaca", 5, "u"),
            ],
            "steps": [
                "Precalentar el horno a 220°C.",
                "Extender la masa y cubrir con tomate.",
                "Agregar mozzarella y hornear por 15 minutos.",
                "Decorar con albahaca fresca y servir.",
            ],
            "tags": ["Italiana", "Vegetariana"]
        },
        {
            "title": "Ramen Japonés",
            "description": "Sopa de fideos japonesa con caldo profundo y toppings.",
            "time_required": timedelta(minutes=90),
            "servings": 1,
            "ingredients": [
                ("Fideos ramen", 100, "gr"),
                ("Caldo de pollo", 500, "ml"),
                ("Huevo cocido", 1, "u"),
                ("Cebollín", 10, "gr"),
            ],
            "steps": [
                "Hervir el caldo a fuego medio.",
                "Cocinar los fideos y escurrir.",
                "Servir los fideos con caldo, huevo y cebollín.",
            ],
            "tags": ["Japonesa", "Sopa"]
        },
        {
            "title": "Panqueques Americanos",
            "description": "Panqueques suaves perfectos para el desayuno.",
            "time_required": timedelta(minutes=20),
            "servings": 4,
            "ingredients": [
                ("Harina", 200, "gr"),
                ("Leche", 250, "ml"),
                ("Huevos", 2, "u"),
                ("Polvo de hornear", 1, "cdta"),
            ],
            "steps": [
                "Mezclar todos los ingredientes.",
                "Calentar sartén y verter porciones.",
                "Cocinar hasta dorar y voltear.",
            ],
            "tags": ["Desayuno", "Fácil"]
        },
        {
            "title": "Paella Valenciana",
            "description": "Plato tradicional español con arroz, mariscos y pollo.",
            "time_required": timedelta(minutes=75),
            "servings": 6,
            "ingredients": [
                ("Arroz", 300, "gr"),
                ("Pollo", 200, "gr"),
                ("Mejillones", 150, "gr"),
                ("Pimiento rojo", 1, "u"),
            ],
            "steps": [
                "Sofreír el pollo y verduras.",
                "Agregar arroz y caldo.",
                "Cocinar hasta que el arroz esté listo y decorar con mariscos.",
            ],
            "tags": ["Española", "Tradicional"]
        },
        {
            "title": "Ensalada César",
            "description": "Lechuga con pollo, aderezo césar y crutones.",
            "time_required": timedelta(minutes=15),
            "servings": 2,
            "ingredients": [
                ("Lechuga romana", 1, "u"),
                ("Pechuga de pollo", 150, "gr"),
                ("Crutones", 50, "gr"),
                ("Aderezo César", 60, "ml"),
            ],
            "steps": [
                "Cortar la lechuga y el pollo cocido.",
                "Mezclar todo con aderezo y añadir crutones.",
            ],
            "tags": ["Ensalada", "Ligera"]
        },
        {
            "title": "Hamburguesa Clásica",
            "description": "Hamburguesa con carne, queso, lechuga y tomate.",
            "time_required": timedelta(minutes=25),
            "servings": 1,
            "ingredients": [
                ("Pan de hamburguesa", 1, "u"),
                ("Carne molida", 150, "gr"),
                ("Queso cheddar", 1, "u"),
                ("Lechuga", 1, "hoja"),
                ("Tomate", 2, "rodajas"),
            ],
            "steps": [
                "Formar y cocinar la carne.",
                "Armar la hamburguesa con todos los ingredientes.",
            ],
            "tags": ["Americana", "Rápida"]
        },
        {
            "title": "Sopa de Lentejas",
            "description": "Sopa nutritiva de lentejas con verduras.",
            "time_required": timedelta(minutes=60),
            "servings": 4,
            "ingredients": [
                ("Lentejas", 200, "gr"),
                ("Zanahoria", 1, "u"),
                ("Papa", 1, "u"),
                ("Cebolla", 1, "u"),
            ],
            "steps": [
                "Cocinar lentejas con agua.",
                "Añadir verduras picadas y hervir hasta ablandar.",
            ],
            "tags": ["Vegetariana", "Sopa"]
        },
        {
            "title": "Tacos Mexicanos",
            "description": "Tortillas rellenas de carne, cebolla y cilantro.",
            "time_required": timedelta(minutes=30),
            "servings": 3,
            "ingredients": [
                ("Tortillas", 3, "u"),
                ("Carne asada", 200, "gr"),
                ("Cebolla", 1, "u"),
                ("Cilantro", 10, "gr"),
            ],
            "steps": [
                "Calentar las tortillas.",
                "Rellenar con carne, cebolla y cilantro.",
            ],
            "tags": ["Mexicana", "Picante"]
        },
        {
            "title": "Sushi de Salmón",
            "description": "Rollos de arroz con salmón y alga nori.",
            "time_required": timedelta(minutes=50),
            "servings": 2,
            "ingredients": [
                ("Arroz para sushi", 150, "gr"),
                ("Salmón", 100, "gr"),
                ("Alga nori", 2, "u"),
                ("Vinagre de arroz", 20, "ml"),
            ],
            "steps": [
                "Cocinar el arroz y enfriar con vinagre.",
                "Enrollar con salmón en alga nori.",
            ],
            "tags": ["Japonesa", "Avanzada"]
        },
        {
            "title": "Shakshuka",
            "description": "Huevos escalfados en salsa de tomate picante.",
            "time_required": timedelta(minutes=35),
            "servings": 2,
            "ingredients": [
                ("Huevos", 4, "u"),
                ("Tomate triturado", 200, "ml"),
                ("Pimiento", 1, "u"),
                ("Ajo", 2, "dientes"),
            ],
            "steps": [
                "Cocinar salsa con ajo, tomate y pimiento.",
                "Agregar huevos y cocinar a fuego lento.",
            ],
            "tags": ["Mediterránea", "Vegetariana"]
        },
        {
            "title": "Curry de Garbanzos",
            "description": "Garbanzos cocinados con especias y leche de coco.",
            "time_required": timedelta(minutes=40),
            "servings": 4,
            "ingredients": [
                ("Garbanzos cocidos", 300, "gr"),
                ("Leche de coco", 200, "ml"),
                ("Curry en polvo", 1, "cda"),
                ("Cebolla", 1, "u"),
            ],
            "steps": [
                "Sofreír cebolla y curry.",
                "Agregar garbanzos y leche de coco, cocinar 20 minutos.",
            ],
            "tags": ["India", "Vegano"]
        },
        {
            "title": "Falafel",
            "description": "Croquetas de garbanzo típicas de Oriente Medio.",
            "time_required": timedelta(minutes=60),
            "servings": 4,
            "ingredients": [
                ("Garbanzos remojados", 250, "gr"),
                ("Perejil", 30, "gr"),
                ("Ajo", 2, "dientes"),
                ("Comino", 1, "cdta"),
            ],
            "steps": [
                "Triturar todo hasta formar una masa.",
                "Formar bolitas y freír.",
            ],
            "tags": ["Vegano", "Oriental"]
        },
        {
            "title": "Lasaña",
            "description": "Pasta al horno con carne, salsa y queso.",
            "time_required": timedelta(minutes=80),
            "servings": 6,
            "ingredients": [
                ("Láminas de lasaña", 6, "u"),
                ("Carne molida", 400, "gr"),
                ("Salsa bechamel", 300, "ml"),
                ("Queso rallado", 150, "gr"),
            ],
            "steps": [
                "Preparar capas de pasta, carne y salsa.",
                "Hornear por 40 minutos.",
            ],
            "tags": ["Italiana", "Completa"]
        },
        {
            "title": "Crepes Dulces",
            "description": "Finas tortitas para rellenar con dulce.",
            "time_required": timedelta(minutes=25),
            "servings": 3,
            "ingredients": [
                ("Harina", 100, "gr"),
                ("Leche", 200, "ml"),
                ("Huevos", 2, "u"),
                ("Azúcar", 2, "cda"),
            ],
            "steps": [
                "Mezclar ingredientes.",
                "Verter en sartén y cocinar por ambos lados.",
            ],
            "tags": ["Postre", "Dulce"]
        },
        {
            "title": "Hummus",
            "description": "Puré de garbanzos con tahini y limón.",
            "time_required": timedelta(minutes=10),
            "servings": 4,
            "ingredients": [
                ("Garbanzos cocidos", 200, "gr"),
                ("Tahini", 2, "cda"),
                ("Limón", 1, "u"),
                ("Ajo", 1, "diente"),
            ],
            "steps": [
                "Triturar todos los ingredientes hasta obtener una pasta suave.",
            ],
            "tags": ["Vegano", "Dip"]
        },
    ]

        for data in recetas:
            receta = Recipe.objects.create(
                title=data["title"],
                description=data["description"],
                time_required=data["time_required"],
                servings=data["servings"],
                author=autor
            )

            for ing in data["ingredients"]:
                ingrediente, _ = Ingredient.objects.get_or_create(name=ing[0])
                RecipeIngredient.objects.create(
                    recipe=receta,
                    ingredient=ingrediente,
                    quantity=ing[1],
                    measurement=ing[2]
                )

            for i, paso in enumerate(data["steps"], start=1):
                Step.objects.create(recipe=receta, step_number=i, description=paso)

            for tag_name in data.get("tags", []):
                try:
                    tag = Tag.objects.get(name=tag_name)
                    receta.tags.add(tag)
                except Tag.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"⚠️  Tag '{tag_name}' no existe y no será añadida."))

            self.stdout.write(self.style.SUCCESS(f"✅ Receta creada: {receta.title}"))
