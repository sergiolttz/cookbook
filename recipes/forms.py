from django import forms
from .models import Recipe, Ingredient, RecipeIngredient, Rating
from .widgets import RecipeDurationWidget

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect(choices=Rating.RATING_CHOICES),
        }

class RecipeForm(forms.ModelForm):
    time_required = forms.DurationField(widget=RecipeDurationWidget())

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'image', 'time_required', 'servings', 'ingredients']  # Elimina 'calification'

    def clean_time_required(self):
        time_required = self.cleaned_data['time_required']
        if time_required is not None:
            return time_required
        else:
            return None

class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity', 'measurement']