from django.db import models
from django.contrib.auth.models import User

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    tag_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    image = models.ImageField(upload_to="images/", default="images/default.jpg")
    time_required = models.DurationField()
    servings = models.PositiveIntegerField(default=1)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True) 

    def __str__(self):
        return self.title


class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1 estrella'),
        (2, '2 estrellas'),
        (3, '3 estrellas'),
        (4, '4 estrellas'),
        (5, '5 estrellas'),
    ]

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)

    class Meta:
        unique_together = ('recipe', 'user')

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
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default="profile_pics/default.jpg")
    favorite_recipes = models.ManyToManyField('Recipe', related_name='favorited_by', blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
