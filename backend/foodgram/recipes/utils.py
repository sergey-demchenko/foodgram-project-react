from django.apps import apps
from django.db.models import F, Sum


def download_shopping_list(user):
    shopping_items = "Cписок покупок:"
    Ingredient = apps.get_model('recipes', 'Ingredient')
    ingredients = (
        Ingredient.objects.filter(recipe__recipe__in_carts__user=user)
        .values('name', measurement=F('measurement_unit'))
        .annotate(amount=Sum('recipe__amount'))
    )
    ing_list = (
        f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}'
        for ing in ingredients
    )
    shopping_items.extend(ing_list)
