from django.urls import path
from .views import recipe_list, recipe_detail  # Importa ambas vistas

urlpatterns = [
    path('', recipe_list, name='recipes-list'),
    path('recipes/<int:pk>/', recipe_detail, name='recipe-detail'), #agrega la url para el detalle
]