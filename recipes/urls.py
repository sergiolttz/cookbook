from django.urls import path
from .views import recipe_list, recipe_detail, recipe_create, recipe_update, recipe_delete, recipe_pdf

urlpatterns = [
    path('', recipe_list, name='recipes-list'),
    path('recipes/<int:pk>/', recipe_detail, name='recipe-detail'),
    path('recipes/create/', recipe_create, name='recipe-create'),
    path('recipes/<int:pk>/update/', recipe_update, name='recipe-update'),
    path('recipes/<int:pk>/delete/', recipe_delete, name='recipe-delete'),
    path('recipes/<int:pk>/pdf/', recipe_pdf, name='recipe-pdf'),
]