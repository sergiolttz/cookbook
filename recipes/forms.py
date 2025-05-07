from django import forms
from .models import Recipe, RecipeIngredient, Rating, UserProfile
from .widgets import RecipeDurationWidget
import datetime
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError




class RecipeForm(forms.ModelForm):
    time_required = forms.DurationField(widget=RecipeDurationWidget())

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'image', 'time_required', 'servings']
        exclude = ['ingredients'] 
        widgets = {
            'image': forms.FileInput(attrs={'id': 'upload-button', 'style': 'display: none;'}),
        }


    def clean_time_required(self):
        time_required = self.cleaned_data['time_required']
        if time_required is not None:
            # Convierte microsegundos a timedelta
            return datetime.timedelta(microseconds=time_required.total_seconds() * 1000000)
        else:
            return None
        
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if image and hasattr(image, 'size'):
            if image.size > 2 * 1024 * 1024:  # 2 MB
                raise forms.ValidationError("La imagen no puede superar los 2MB.")
        
        return image

class IngredientForm(forms.Form):
    ingredient_name = forms.CharField(max_length=100)
    ingredient_quantity = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0
    )
    ingredient_measurement = forms.ChoiceField(
        choices=RecipeIngredient.MEASUREMENT_CHOICES,
        required=False
    )

class StepForm(forms.Form):
    step_description = forms.CharField(widget=forms.Textarea)

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect(choices=Rating.RATING_CHOICES),
        }

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
    
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña actual'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Nueva contraseña'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar nueva contraseña'
    )

    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']