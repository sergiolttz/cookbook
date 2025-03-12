from django.shortcuts import render, get_object_or_404, redirect
from .models import Recipe
from .forms import RecipeForm

def recipe_list(request):
    """Vista para mostrar la lista de recetas."""
    recipe_list = Recipe.objects.all()
    return render(request, 'recipes-list.html', {'recipe_list': recipe_list})

def recipe_detail(request, pk):
    """Vista para mostrar el detalle de una receta."""
    recipe = get_object_or_404(Recipe, pk=pk)    
    return render(request, 'recipe-detail.html', {'recipe': recipe})

def recipe_create(request):
    """Vista para crear una nueva receta."""
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            form.save_m2m() #para guardar las relaciones many to many
            return redirect('recipe-detail', pk=recipe.pk)
    else:
        form = RecipeForm()
    return render(request, 'recipe-create.html', {'form': form})