from django.shortcuts import render, get_object_or_404, redirect
from .forms import RecipeForm, RecipeForm, IngredientForm, RecipeIngredientForm, StepForm, RatingForm, UserProfileForm
from .models import Recipe, Ingredient, RecipeIngredient, Step, Rating, UserProfile, Tag
import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.contrib.auth.models import User
import datetime
from django.forms import formset_factory
from django import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.staticfiles.storage import staticfiles_storage


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

    quick_recipes_with_ratings = []
    quick_recipes = []
    for recipe in recipes:
        if recipe.time_required is not None:
            # Convierte microsegundos a timedelta
            td = datetime.timedelta(microseconds=recipe.time_required.total_seconds() * 1000000)
            if td <= datetime.timedelta(minutes=12):
                quick_recipes.append(recipe)
                avg_rating = Rating.objects.filter(recipe=recipe).aggregate(Avg('rating'))['rating__avg']
                quick_recipes_with_ratings.append({'recipe': recipe, 'avg_rating': avg_rating})

    few_ingredients_recipes_with_ratings = []
    few_ingredients_recipes = [recipe for recipe in recipes if recipe.recipeingredient_set.count() < 3]
    for recipe in few_ingredients_recipes:
        avg_rating = Rating.objects.filter(recipe=recipe).aggregate(Avg('rating'))['rating__avg']
        few_ingredients_recipes_with_ratings.append({'recipe': recipe, 'avg_rating': avg_rating})

    latest_recipes_with_ratings = []
    latest_recipes = Recipe.objects.order_by('-created_at')[:3]  # Obtiene las 3 últimas recetas
    for recipe in latest_recipes:
        avg_rating = Rating.objects.filter(recipe=recipe).aggregate(Avg('rating'))['rating__avg']
        latest_recipes_with_ratings.append({'recipe': recipe, 'avg_rating': avg_rating})

    favorite_recipes = []
    user_profile = None  # Inicializa user_profile
    if request.user.is_authenticated:
        favorite_recipes = request.user.profile.favorite_recipes.all()
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass

    return render(request, 'home.html', {
        'recipes': recipes,
        'quick_recipes_with_ratings': quick_recipes_with_ratings[:3],
        'few_ingredients_recipes_with_ratings': few_ingredients_recipes_with_ratings[:3],
        'favorite_recipes': favorite_recipes,
        'latest_recipes_with_ratings': latest_recipes_with_ratings,
        'has_more_quick_recipes': len(quick_recipes) > 3,
        'has_more_few_ingredients_recipes': len(few_ingredients_recipes) > 3,
        'user_profile': user_profile,
    })

def recipe_list(request):
    """Vista para mostrar la lista de recetas con búsqueda, ordenamiento y filtro por etiquetas con paginación."""
    query = request.GET.get('q')
    sort_by = request.GET.get('sort')
    order = request.GET.get('order', 'asc')
    selected_tags = request.GET.getlist('tags')  # Obtener las etiquetas seleccionadas

    recipes = Recipe.objects.all()

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if selected_tags:
        recipes = recipes.filter(tags__in=selected_tags).distinct()

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

    # Paginación
    paginator = Paginator(recipes, 9)  # Mostrar 9 recetas por página
    page = request.GET.get('page')

    try:
        recipes_page = paginator.page(page)
    except PageNotAnInteger:
        # Si page no es un entero, entrega la primera página.
        recipes_page = paginator.page(1)
    except EmptyPage:
        # Si page está fuera de rango (ej. 9999), entrega la última página.
        recipes_page = paginator.page(paginator.num_pages)

    # Calcula la calificación promedio para las recetas en la página actual
    recipes_with_ratings = []
    for recipe in recipes_page.object_list:
        avg_rating = Rating.objects.filter(recipe=recipe).aggregate(Avg('rating'))['rating__avg']
        recipes_with_ratings.append({'recipe': recipe, 'avg_rating': avg_rating})

    # Obtener tipos de etiquetas y etiquetas asociadas
    tag_types = Tag.objects.values_list('tag_type', flat=True).distinct()
    all_tags = Tag.objects.all()  # Obtener todas las etiquetas

    user_profile = None  # Inicializa user_profile
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass

    return render(request, 'recipes-list.html', {
        'recipes_with_ratings': recipes_with_ratings,
        'recipes_page': recipes_page,  # Pasar el objeto Page a la plantilla
        'query': query,
        'sort_by': sort_by,
        'order': order,
        'tag_types': tag_types,
        'all_tags': all_tags,  # Pasar todas las etiquetas al contexto
        'selected_tags': selected_tags,
        'user_profile': user_profile,  # Añade user_profile al contexto
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

    user_profile = None  # Inicializa user_profile
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass

    context = {
        'recipe': recipe,
        'average_rating': average_rating,
        'form': form,
        'user_profile': user_profile,  # Añade user_profile al contexto
    }

    return render(request, 'recipe-detail.html', context)

@login_required
def recipe_create(request):
    """Vista para crear una nueva receta."""
    IngredientFormSet = formset_factory(IngredientForm, extra=1)
    StepFormSet = formset_factory(StepForm, extra=1)

    tag_types = Tag.objects.values_list('tag_type', flat=True).distinct()  # new

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        ingredient_formset = IngredientFormSet(request.POST, prefix='ingredients')
        step_formset = StepFormSet(request.POST, prefix='steps')
        selected_tags = request.POST.getlist('tags')  # Obtener etiquetas seleccionadas #new

        if form.is_valid() and ingredient_formset.is_valid() and step_formset.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            # Guardar ingredientes y pasos (como antes)
            for ingredient_form in ingredient_formset:
                if ingredient_form.cleaned_data and ingredient_form.cleaned_data.get('ingredient_name'):
                    ingredient, created = Ingredient.objects.get_or_create(name=ingredient_form.cleaned_data['ingredient_name'])
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity=ingredient_form.cleaned_data['ingredient_quantity'],
                        measurement=ingredient_form.cleaned_data['ingredient_measurement']
                    )

            step_number = 1
            for step_form in step_formset:
                if step_form.cleaned_data and step_form.cleaned_data.get('step_description'):
                    Step.objects.create(
                        recipe=recipe,
                        step_number=step_number,
                        description=step_form.cleaned_data['step_description']
                    )
                    step_number += 1

            # Guardar etiquetas seleccionadas
            for tag_id in selected_tags:
                recipe.tags.add(tag_id)

            return redirect('recipe-detail', pk=recipe.pk)
    else:
        form = RecipeForm()
        ingredient_formset = IngredientFormSet(prefix='ingredients')
        step_formset = StepFormSet(prefix='steps')
        ingredient_empty_form_html = ingredient_formset.empty_form.as_p
        step_empty_form_html = step_formset.empty_form.as_p

    user_profile = None  # Inicializa user_profile
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass

    return render(request, 'recipe-create.html', {
        'form': form,
        'ingredient_formset': ingredient_formset,
        'step_formset': step_formset,
        'ingredient_empty_form_html': ingredient_empty_form_html,
        'step_empty_form_html': step_empty_form_html,
        'tag_types': tag_types,  # new
        'all_tags': Tag.objects.all(),  # new
        'user_profile': user_profile,  # Añade user_profile al contexto
    })

register = template.Library()

@register.filter(name='modulo')
def modulo(value, arg):
    return value % arg

@login_required
def recipe_update(request, pk):
    """Vista para editar una receta existente."""
    recipe = get_object_or_404(Recipe, pk=pk)

    if recipe.author != request.user:
        return redirect('recipe-detail', pk=recipe.pk)

    tag_types = Tag.objects.values_list('tag_type', flat=True).distinct()  # new

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        selected_tags = request.POST.getlist('tags')  # new

        if form.is_valid():
            form.save()
            recipe.tags.clear()  # Limpiar etiquetas existentes #new
            for tag_id in selected_tags:  # new
                recipe.tags.add(tag_id)  # new
            return redirect('recipe-detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)

    user_profile = None  # Inicializa user_profile
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass

    return render(request, 'recipe-update.html', {
        'form': form,
        'recipe': recipe,
        'tag_types': tag_types,
        'all_tags': Tag.objects.all(),
        'user_profile': user_profile,  # Añade user_profile al contexto
    })

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

    user_profile = None  # Inicializa user_profile
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass

    return render(request, 'recipe-delete.html', {'recipe': recipe, 'user_profile': user_profile})

def recipe_pdf(request, pk):
    """Vista para generar un PDF de la receta."""
    recipe = get_object_or_404(Recipe, pk=pk)

    image_url = request.build_absolute_uri(recipe.image.url) if recipe.image else None
    logo_url = request.build_absolute_uri(staticfiles_storage.url('images/logo.png'))

    html_string = render_to_string('recipe-pdf.html', {'recipe': recipe, 'image_url': image_url, 'logo_url': logo_url})

    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
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

    user_profile = None  # Inicializa user_profile
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass

    return render(request, 'edit-profile.html', {'form': form, 'user_profile': user_profile})

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
    user_profile = None  # Inicializa user_profile
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass
    return render(request, 'edit-profile.html', {'user_profile': user_profile})