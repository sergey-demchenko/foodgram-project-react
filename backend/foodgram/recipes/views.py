from django.db.models import Sum
from django.http import HttpResponse
from .models import RecipeIngredient
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from users.permissions import IsAuthorOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from .mixins import add_del_recipe
from .models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from .pagination import SimplePagination
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingListSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """ Отображение рецептов. """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = RecipeFilter
    pagination_class = SimplePagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return CreateRecipeSerializer
        return RecipeSerializer

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        """ Добавление и удаление рецепта из избранного. """
        model = Favorite
        serializer = FavoriteSerializer
        return add_del_recipe(request, pk, serializer, model)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated],)
    def shopping_cart(self, request, pk):
        """ Добавление и удаление рецепта из списка покупок. """
        model = ShoppingList
        serializer = ShoppingListSerializer
        return add_del_recipe(request, pk, serializer, model)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """ Скачать список покупок. """
        try:
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
            response = HttpResponse(
                shopping_items,
                'Content-Type: application/pdf'
            )
            response[
                'Content-Disposition'
            ] = f'attachment; filename="{file}.pdf"'
            return response
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ Отображение ингредиентов. """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter,)
    search_fields = ['^name', ]


class TagViewSet(viewsets.ModelViewSet):
    """ Отображение тегов. """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
