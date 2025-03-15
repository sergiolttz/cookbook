"""

from django import forms
from .models import Recipe, Ingredient, RecipeIngredient
from .widgets import RecipeDurationWidget
from django.core.validators import MinValueValidator

class RecipeForm(forms.ModelForm):
    time_required = forms.DurationField(widget=RecipeDurationWidget())
    ingredient_name = forms.CharField(max_length=100, required=False)
    ingredient_quantity = forms.DecimalField(
        max_digits=4,
        decimal_places=1,
        required=False,
        validators=[MinValueValidator(0)]
    )
    ingredient_measurement = forms.ChoiceField(choices=RecipeIngredient.MEASUREMENT_CHOICES, required=False)

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'image', 'time_required', 'servings', 'calification']
        exclude = ['ingredient_name', 'ingredient_quantity', 'ingredient_measurement']

    def save(self, commit=True):
        recipe = super().save(commit=False)  # Guarda la receta sin confirmación inmediata

        ingredient_name = self.cleaned_data.get('ingredient_name')
        ingredient_quantity = self.cleaned_data.get('ingredient_quantity')
        ingredient_measurement = self.cleaned_data.get('ingredient_measurement')

        if ingredient_name and ingredient_quantity and ingredient_measurement:
            ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=ingredient_quantity, measurement=ingredient_measurement)

        if commit:
            recipe.save()  # Confirma el guardado de la receta si se solicita

        return recipe
"""

from django import forms
from .models import Recipe
from .widgets import RecipeDurationWidget
from django.core.validators import MinValueValidator

class RecipeForm(forms.ModelForm):
    time_required = forms.DurationField(widget=RecipeDurationWidget())

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'image', 'time_required', 'servings', 'calification']