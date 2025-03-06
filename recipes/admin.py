from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient, Step

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

admin.site.register(Ingredient, IngredientAdmin)

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

class StepInline(admin.TabularInline):
    model = Step
    extra = 1

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'calification')
    search_fields = ('title', 'description')
    list_filter = ('author',)
    inlines = [RecipeIngredientInline, StepInline]
    fieldsets = (
        ('Información básica', {
            'fields': ('title', 'description', 'author')
        }),
        ('Detalles de la receta', {
            'fields': ('image', 'time_required', 'servings', 'calification')
        }),
    )

admin.site.register(Recipe, RecipeAdmin)