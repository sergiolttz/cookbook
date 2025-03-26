from django.urls import path
from .views import recipe_list, recipe_detail, recipe_create, recipe_update, recipe_delete, recipe_pdf, user_profile, add_favorite, remove_favorite

urlpatterns = [
    path('', recipe_list, name='recipes-list'),
    path('recipes/<int:pk>/', recipe_detail, name='recipe-detail'),
    path('recipes/create/', recipe_create, name='recipe-create'),
    path('recipes/<int:pk>/update/', recipe_update, name='recipe-update'),
    path('recipes/<int:pk>/delete/', recipe_delete, name='recipe-delete'),
    path('recipes/<int:pk>/pdf/', recipe_pdf, name='recipe-pdf'),
    path('profile/<str:username>/', user_profile, name='user_profile'),
    path('add_favorite/<int:recipe_id>/', add_favorite, name='add_favorite'),
    path('remove_favorite/<int:recipe_id>/', remove_favorite, name='remove_favorite'),
]