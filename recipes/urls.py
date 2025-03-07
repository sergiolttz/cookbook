from django.urls import path
from .views import recipe_list  # Importa la función recipe_list

urlpatterns = [
    path('', recipe_list, name='recipes-list'),
]