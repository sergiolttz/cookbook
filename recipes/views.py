from django.shortcuts import render
from .models import Recipe

def recipe_list(request):
    """
    Vista para mostrar la lista de recetas.
    """
    recipes = Recipe.objects.all()  # Obtiene todas las recetas de la base de datos
    context = {
        'recipe_list': recipes,  # Pasa la lista de recetas a la plantilla
    }
    return render(request, 'recipes-list.html', context)