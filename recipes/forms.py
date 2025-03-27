from django import forms
from .models import Recipe, RecipeIngredient, Rating, UserProfile
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


class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(label='Correo electrónico', required=True)

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'country', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        user_profile = super(UserProfileForm, self).save(commit=False)
        if commit:
            user_profile.save()
            user = user_profile.user
            user.email = self.cleaned_data['email']
            user.save()
        return user_profile