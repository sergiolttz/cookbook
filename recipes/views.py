from django.shortcuts import render, get_object_or_404, redirect
from .forms import RecipeForm, RecipeForm, IngredientForm, RecipeIngredientForm, StepForm, RatingForm, UserProfileForm
from .models import Recipe, Ingredient, RecipeIngredient, Step, Rating, UserProfile
import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.contrib.auth.models import User
import datetime
from django.forms import formset_factory, inlineformset_factory
from django import template



def home(request):
    """Vista para la página de inicio."""
    query = request.GET.get('q')  # Obtener la consulta de búsqueda

    if query:
        # Si hay una consulta, filtrar las recetas por título o descripción
        recipes = Recipe.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        # Si no hay consulta, obtener todas las recetas
        recipes = Recipe.objects.all()

    quick_recipes = []
    for recipe in recipes:
        if recipe.time_required is not None:
            # Convierte microsegundos a timedelta
            td = datetime.timedelta(microseconds=recipe.time_required.total_seconds() * 1000000)
            if td <= datetime.timedelta(minutes=12):
                quick_recipes.append(recipe)

    few_ingredients_recipes = [recipe for recipe in recipes if recipe.recipeingredient_set.count() < 3]

    favorite_recipes = []
    if request.user.is_authenticated:
        favorite_recipes = request.user.profile.favorite_recipes.all()

    latest_recipes = Recipe.objects.order_by('-created_at')[:3]  # Obtiene las 3 últimas recetas

    return render(request, 'home.html', {
        'recipes': recipes,
        'quick_recipes': quick_recipes[:3],  # Muestra solo las primeras 3 recetas rápidas
        'few_ingredients_recipes': few_ingredients_recipes[:3],  # Muestra solo las primeras 3 recetas con pocos ingredientes
        'favorite_recipes': favorite_recipes,
        'latest_recipes': latest_recipes,  # Muestra las 3 últimas recetas
        'has_more_quick_recipes': len(quick_recipes) > 3,  # Indica si hay más recetas rápidas
        'has_more_few_ingredients_recipes': len(few_ingredients_recipes) > 3,  # Indica si hay más recetas con pocos ingredientes
    })

def recipe_list(request):
    """Vista para mostrar la lista de recetas con búsqueda y ordenamiento."""
    query = request.GET.get('q')  # Obtener la consulta de búsqueda
    sort_by = request.GET.get('sort')  # Obtener el parámetro de ordenamiento
    order = request.GET.get('order', 'asc')  # Obtener el parámetro de ordenamiento (ascendente/descendente)

    recipes = Recipe.objects.all()

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if sort_by == 'rating':
        if order == 'asc':
            recipes = recipes.annotate(avg_rating=Avg('rating__rating')).order_by('avg_rating')
        else:
            recipes = recipes.annotate(avg_rating=Avg('rating__rating')).order_by('-avg_rating')
    elif sort_by == 'duration':
        if order == 'asc':
            recipes = recipes.order_by('time_required')
        else:
            recipes = recipes.order_by('-time_required')
    elif sort_by == 'ingredients':
        if order == 'asc':
            recipes = recipes.annotate(ingredient_count=Count('recipeingredient')).order_by('ingredient_count')
        else:
            recipes = recipes.annotate(ingredient_count=Count('recipeingredient')).order_by('-ingredient_count')

    # Calcula la calificación promedio para cada receta
    recipes_with_ratings = []
    for recipe in recipes:
        avg_rating = Rating.objects.filter(recipe=recipe).aggregate(Avg('rating'))['rating__avg']
        recipes_with_ratings.append({'recipe': recipe, 'avg_rating': avg_rating})

    return render(request, 'recipes-list.html', {
        'recipes_with_ratings': recipes_with_ratings,
        'query': query,
        'sort_by': sort_by,
        'order': order,
    })

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
    IngredientFormSet = formset_factory(IngredientForm, extra=1)
    StepFormSet = formset_factory(StepForm, extra=1)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)  # Inicializar form aquí
        ingredient_formset = IngredientFormSet(request.POST, prefix='ingredients')
        step_formset = StepFormSet(request.POST, prefix='steps')

        if form.is_valid() and ingredient_formset.is_valid() and step_formset.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            # Guardar ingredientes
            for ingredient_form in ingredient_formset:
                if ingredient_form.cleaned_data and ingredient_form.cleaned_data.get('ingredient_name'):
                    ingredient, created = Ingredient.objects.get_or_create(name=ingredient_form.cleaned_data['ingredient_name'])
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity=ingredient_form.cleaned_data['ingredient_quantity'],
                        measurement=ingredient_form.cleaned_data['ingredient_measurement']
                    )

            # Guardar pasos
            step_number = 1  # Inicializar el número de paso
            for step_form in step_formset:
                if step_form.cleaned_data and step_form.cleaned_data.get('step_description'):
                    Step.objects.create(
                        recipe=recipe,
                        step_number=step_number,
                        description=step_form.cleaned_data['step_description']
                    )
                    step_number += 1  # Incrementar el número de paso

            return redirect('recipe-detail', pk=recipe.pk)
    else:
        form = RecipeForm() # Inicializar form aquí tambien
        ingredient_formset = IngredientFormSet(prefix='ingredients')
        step_formset = StepFormSet(prefix='steps')

        # Renderizar los formularios vacíos como HTML
        ingredient_empty_form_html = ingredient_formset.empty_form.as_p
        step_empty_form_html = step_formset.empty_form.as_p

    return render(request, 'recipe-create.html', {
        'form': form,
        'ingredient_formset': ingredient_formset,
        'step_formset': step_formset,
        'ingredient_empty_form_html': ingredient_empty_form_html,
        'step_empty_form_html': step_empty_form_html,
    })

register = template.Library()

@register.filter(name='modulo')
def modulo(value, arg):
    return value % arg

@login_required
def recipe_update(request, pk):
    """Vista para editar una receta existente."""
    recipe = get_object_or_404(Recipe, pk=pk)

    # Verifica si el usuario actual es el autor de la receta
    if recipe.author != request.user:
        return redirect('recipe-detail', pk=recipe.pk)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
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

    return render(request, 'user-profile.html', context)

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
    return render(request, 'edit-profile.html', {'form': form})

@login_required
def deactivate_account(request):
    """Vista para desactivar la cuenta del usuario."""
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()

        """Desactiva las recetas subidas por el usuario."""
        Recipe.objects.filter(author=user).update(is_active=False)

        """Cierra la sesión del usuario."""
        from django.contrib.auth import logout
        logout(request)

        return redirect('recipes-list')
    return redirect('edit_profile')