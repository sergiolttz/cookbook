from django.urls import path
from .views import recipe_list, recipe_detail, recipe_create  

urlpatterns = [
    path('', recipe_list, name='recipes-list'),
    path('recipes/<int:pk>/', recipe_detail, name='recipe-detail'),
    path('recipes/create/', recipe_create, name='recipe-create'),

]