from django import forms
from .models import Recipe
from .widgets import RecipeDurationWidget

class RecipeForm(forms.ModelForm):
    time_required = forms.DurationField(widget=RecipeDurationWidget())

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'image', 'time_required', 'servings', 'calification']