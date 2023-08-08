from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        ReadOnlyField, SerializerMethodField)

from users.serializers import CustomUserSerializer
from .fields import Base64ImageField, Hex2NameColor
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingList, Tag)


class TagSerializer(ModelSerializer):
    """ Сериализатор тега. """

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'slug'
        ]


class RecipeIngredientSerializer(ModelSerializer):
    """ Сериализатор связи рецепта и ингредиента. """

    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = [
            'id',
            'name',
            'amount',
            'measurement_unit'
        ]


class IngredientSerializer(ModelSerializer):
    """ Сериализатор ингредиента. """

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit'
        ]


class RecipeSerializer(ModelSerializer):
    """ Сериализатор рецепта. """

    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()


class AddIngredientRecipeSerializer(ModelSerializer):
    """ Сериализатор добавления ингредиента. """

    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = [
            'id',
            'amount'
        ]


class CreateRecipeSerializer(ModelSerializer):
    """ Сериализатор создания рецепта. """

    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def validate_ingredients(self, data):
        ingredient_data = self.initial_data.get('ingredients')
        if ingredient_data:
            ingredient_int = set()
            for ingredient in ingredient_data:
                ingredient_obj = get_object_or_404(
                    Ingredient, id=ingredient['id']
                )
                if ingredient_obj in ingredient_int:
                    raise serializers.ValidationError(
                        'Ингредиенты не должны повторяться'
                    )
                ingredient_int.add(ingredient_obj)
        return data

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient['id']
                ),
                recipe=recipe, amount=ingredient.pop('amount')
            )
            for ingredient in ingredients
        ])

    def create_tags(self, tags, recipe):
        RecipeTag.objects.bulk_create([
            RecipeTag(recipe=recipe, tag=tag)
            for tag in tags
        ])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        RecipeTag.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        self.create_ingredients(ingredients, instance)
        self.create_tags(tags, instance)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class FavoriteSerializer(RecipeSerializer):
    """ Сериализатор избранного. """

    name = ReadOnlyField()
    cooking_time = ReadOnlyField()

    class Meta(RecipeSerializer.Meta):
        fields = (
            'id',
            'name',
            'cooking_time',
        )

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже в избранном',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class ShoppingListSerializer(RecipeSerializer):
    """ Сериализатор списка покупок. """

    name = ReadOnlyField()
    cooking_time = ReadOnlyField()

    class Meta(RecipeSerializer.Meta):
        fields = (
            'id',
            'name',
            'cooking_time',
        )

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if ShoppingList.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                'Рецепт уже в корзине',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
