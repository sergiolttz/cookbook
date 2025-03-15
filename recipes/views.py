from django.shortcuts import render, get_object_or_404, redirect
from .forms import RecipeForm
from .models import Recipe, Ingredient, RecipeIngredient, Step

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

            # Manejar la creación de múltiples ingredientes
            ingredient_names = request.POST.getlist('ingredient_name')
            ingredient_quantities = request.POST.getlist('ingredient_quantity')
            ingredient_measurements = request.POST.getlist('ingredient_measurement')

            for i in range(len(ingredient_names)):
                ingredient_name = ingredient_names[i]
                ingredient_quantity = ingredient_quantities[i]
                ingredient_measurement = ingredient_measurements[i]

                if ingredient_name and ingredient_quantity and ingredient_measurement:
                    ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity=ingredient_quantity,
                        measurement=ingredient_measurement
                    )

            # Manejar la creación de pasos
            step_descriptions = request.POST.getlist('step_description')

            for i, description in enumerate(step_descriptions):
                if description:
                    Step.objects.create(recipe=recipe, step_number=i + 1, description=description)

            return redirect('recipe-detail', pk=recipe.pk)
    else:
        form = RecipeForm()
    return render(request, 'recipe-create.html', {'form': form})