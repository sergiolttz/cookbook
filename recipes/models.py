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
    image = models.ImageField(upload_to="images/", default="images/default.jpg")
    time_required = models.DurationField()
    servings = models.PositiveIntegerField(default=1)
    calification = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    MEASUREMENT_CHOICES = [
            ('gr', 'Gramos'),
            ('kg', 'Kilogramos'),
            ('ml', 'Mililitros'),
            ('l', 'Litros'),
            ('tz', 'Taza'),
            ('cdta', 'Cucharadita'),
            ('cda', 'Cucharada'),
            ('u', 'Unidad'),
        ]
    measurement = models.CharField(max_length=10, choices=MEASUREMENT_CHOICES)

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