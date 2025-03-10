from django.shortcuts import render, get_object_or_404
from .models import Recipe

def recipe_list(request):
    """Vista para mostrar la lista de recetas."""
    recipe_list = Recipe.objects.all()
    return render(request, 'recipes-list.html', {'recipe_list': recipe_list})

def recipe_detail(request, pk):
    """Vista para mostrar el detalle de una receta."""
    recipe = get_object_or_404(Recipe, pk=pk)    
    return render(request, 'recipe-detail.html', {'recipe': recipe})