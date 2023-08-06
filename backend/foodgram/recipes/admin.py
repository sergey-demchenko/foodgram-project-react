from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingList, Tag)


class IngredientsInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class TagsInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'recipe'
        ]
    search_fields = [
        'user__username',
        'user__email'
        ]
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'measurement_unit'
        ]
    search_fields = ['name']
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'author',
        'favorites'
        ]
    search_fields = [
        'name',
        'author__username',
        'tags'
        ]
    list_filter = ['tags']
    empty_value_display = '-пусто-'
    inlines = (
        IngredientsInLine,
        TagsInline
    )

    @admin.display(description='В избранном')
    def favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    @admin.display(description='Теги')
    def get_tags(self, obj):
        """Отображаем теги для рецепта"""
        return ", ".join(
            [t for t in obj.tags.values_list('name', flat=True)])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        """Отображаем ингредиенты для рецепта"""
        return ", ".join(
            [i for i in obj.ingredients.values_list('name', flat=True)])


@admin.register(ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'recipe'
        ]
    search_fields = [
        'user__username',
        'user__email'
        ]
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    inlines = [
        TagsInline
    ]
    list_display = [
        'id',
        'name',
        'color',
        'slug'
        ]
    search_fields = [
        'name',
        'slug'
        ]
    empty_value_display = '-пусто-'
