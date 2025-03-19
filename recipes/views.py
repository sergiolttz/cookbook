from django.shortcuts import render, get_object_or_404, redirect
from .forms import RecipeForm
from .models import Recipe, Ingredient, RecipeIngredient, Step
import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string

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

def recipe_update(request, pk):
    """Vista para editar una receta existente."""
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            recipe = form.save()

            # Manejar la actualización de ingredientes
            ingredient_names = request.POST.getlist('ingredient_name')
            ingredient_quantities = request.POST.getlist('ingredient_quantity')
            ingredient_measurements = request.POST.getlist('ingredient_measurement')

            # Eliminar ingredientes existentes
            recipe.recipeingredient_set.all().delete()

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

            # Manejar la actualización de pasos
            step_descriptions = request.POST.getlist('step_description')

            # Eliminar pasos existentes
            recipe.steps.all().delete()

            for i, description in enumerate(step_descriptions):
                if description:
                    Step.objects.create(recipe=recipe, step_number=i + 1, description=description)

            return redirect('recipe-detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)

    return render(request, 'recipe-update.html', {'form': form, 'recipe': recipe})

def recipe_delete(request, pk):
    """Vista para eliminar una receta."""
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == 'POST':
        recipe.delete()
        return redirect('recipes-list')

    return render(request, 'recipe-delete.html', {'recipe': recipe})

def recipe_pdf(request, pk):
    """Vista para generar un PDF de la receta."""
    recipe = get_object_or_404(Recipe, pk=pk)

    # Generar la URL absoluta de la imagen
    image_url = request.build_absolute_uri(recipe.image.url) if recipe.image else None

    html_string = render_to_string('recipe-pdf.html', {'recipe': recipe, 'image_url': image_url})

    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe') # Reemplaza con la ruta correcta
    options = {
        'encoding': 'UTF-8',
    }
    pdf = pdfkit.from_string(html_string, False, configuration=config, options=options)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{recipe.title}.pdf"'

    return response