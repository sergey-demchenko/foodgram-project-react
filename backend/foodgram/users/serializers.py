from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.serializers import SerializerMethodField

from recipes.models import Recipe
from .models import Subscription, User


class CustomUserSerializer(UserSerializer):
    """ Сериализатор пользователя. """

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
            ]

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriber.filter(author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя. """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
            ]


class CropRecipeSerializer(serializers.ModelSerializer):
    """ Укороченный сериализатор рецепта. """

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
            ]
        read_only_fields = ['__all__', ]


class SubscribeSerializer(UserSerializer):
    """ Сериализатор подписки. """

    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
            ]
        read_only_fields = [
            'email',
            'username',
            'first_name',
            'last_name'
            ]

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriber.filter(author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return CropRecipeSerializer(recipes, many=True,
                                    context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscription.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на автора',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data
