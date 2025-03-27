from django.shortcuts import render, get_object_or_404, redirect
from .forms import RecipeForm, RatingForm, UserProfileForm
from .models import Recipe, Ingredient, RecipeIngredient, Step, Rating, UserProfile
import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.contrib.auth.models import User


def recipe_list(request):
    """Vista para mostrar la lista de recetas. """
    recipe_list = Recipe.objects.all() 
    recipe_ratings = []
    for recipe in recipe_list:
        ratings = Rating.objects.filter(recipe=recipe)
        average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        recipe_ratings.append({'recipe': recipe, 'average_rating': average_rating})

    return render(request, 'recipes-list.html', {'recipe_ratings': recipe_ratings})

def recipe_detail(request, pk):
    """Vista para mostrar el detalle de una receta y manejar las calificaciones."""
    recipe = get_object_or_404(Recipe, pk=pk)

    # Lógica de calificación
    ratings = Rating.objects.filter(recipe=recipe)
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg']

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating_value = form.cleaned_data['rating']
            existing_rating = Rating.objects.filter(recipe=recipe, user=request.user).first()
            if existing_rating:
                existing_rating.rating = rating_value
                existing_rating.save()
            else:
                Rating.objects.create(recipe=recipe, user=request.user, rating=rating_value)
            # Recalcula el promedio después de guardar la calificación
            ratings = Rating.objects.filter(recipe=recipe)
            average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
    else:
        form = RatingForm()

    context = {
        'recipe': recipe,
        'average_rating': average_rating,
        'form': form,
    }

    return render(request, 'recipe-detail.html', context)

@login_required
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

@login_required
def recipe_update(request, pk):
    """Vista para editar una receta existente."""
    recipe = get_object_or_404(Recipe, pk=pk)

    # Verifica si el usuario actual es el autor de la receta
    if recipe.author != request.user:
        return redirect('recipe-detail', pk=recipe.pk)  # O muestra un mensaje de error

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

@login_required
def recipe_delete(request, pk):
    """Vista para eliminar una receta."""
    recipe = get_object_or_404(Recipe, pk=pk)

    # Verifica si el usuario actual es el autor de la receta
    if recipe.author != request.user:
        return redirect('recipe-detail', pk=recipe.pk)  # O muestra un mensaje de error

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


def user_profile(request, username):
    """Vista para ver el perfil de usuario."""
    user = get_object_or_404(User, username=username)
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    created_recipes = Recipe.objects.filter(author=user)
    favorite_recipes = user_profile.favorite_recipes.all()

    context = {
        'user_profile': user_profile,
        'created_recipes': created_recipes,
        'favorite_recipes': favorite_recipes,
    }

    return render(request, 'user_profile.html', context)

@login_required
def add_favorite(request, recipe_id):
    """Vista para agregar una receta a favoritos."""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile.favorite_recipes.add(recipe)
    return redirect('recipe-detail', pk=recipe.pk)

@login_required
def remove_favorite(request, recipe_id):
    """Vista para eliminar una receta de favoritos."""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile.favorite_recipes.remove(recipe)
    return redirect('recipe-detail', pk=recipe.pk)

@login_required
def edit_profile(request):
    """Vista para editar el perfil del usuario."""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'edit_profile.html', {'form': form})