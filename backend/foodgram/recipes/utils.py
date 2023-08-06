from django.db.models import Sum
from django.http import HttpResponse

from .models import RecipeIngredient


def download_shopping_list(request):
    shopping_items = "Cписок покупок:"
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping__user=request.user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(counter=Sum('amount'))

    for num, ingr in enumerate(ingredients):
        shopping_items += (
            f"\n{ingr['ingredient__name']} - "
            f"{ingr['counter']} {ingr['ingredient__measurement_unit']}"
        )
        if num < ingredients.count() - 1:
            shopping_items += ', '

    file = 'shopping_list'
    response = HttpResponse(shopping_items, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    return response
