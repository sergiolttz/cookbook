from django.db import models
from django.contrib.auth.models import User

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    image = models.ImageField(upload_to="images/")
    time_required = models.CharField(max_length=50)
    servings = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    calification = models.CharField(max_length=50)

    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)  # Cambiado a DecimalField
    MEASUREMENT_CHOICES = [
        ('u', 'Unidades'),
        ('g', 'Gramos'),
        ('kg', 'Kilos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('tz', 'Tazas'),
        ('cdta', 'Cucharaditas'),
        ('cda', 'Cucharadas'),
        ('pz', 'Pizca'),        
        ('oz', 'Onzas'),
        ('lb', 'Libras'),        
    ]
    measurement = models.CharField(max_length=20, choices=MEASUREMENT_CHOICES, default='gramos')

    def __str__(self):
        return f'{self.ingredient.name} en {self.recipe.title}'


class Step(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    step_number = models.PositiveIntegerField()
    description = models.TextField()

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f'{self.recipe.title} - Paso {self.step_number}'