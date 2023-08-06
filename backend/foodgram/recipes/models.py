from django.db import models

from users.models import User


class Ingredient(models.Model):
    """ Модель ингредиента. """

    name = models.CharField(
        verbose_name='Нааименование ингредиента',
        max_length=100,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=10,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='ingredient_unique'
            )
        ]


class Tag(models.Model):
    """ Модель тега """

    name = models.CharField(
        verbose_name='Наименование тега',
        max_length=20
    )
    color = models.CharField(
        verbose_name='Код цвета',
        max_length=8
    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True,
        max_length=100,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ Модель рецепта """

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='Наименование рецепта',
        max_length=100
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/'
    )
    text = models.TextField(
        verbose_name='Описание',
        max_length=500
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient',
        related_name='ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        through='RecipeTag',
        related_name='tags'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    created = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """ Модель связи рецепта и ингредиента. """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_ingredient_unique'
            )
        ]


class RecipeTag(models.Model):
    """ Модель рецепта и тега. """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тег',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='recipe_tag_unique'
            )
        ]


class Favorite(models.Model):
    """ Модель избранное. """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        related_name='favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_unique'
            )
        ]


class ShoppingList(models.Model):
    """ Модель покупок. """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shopping',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shopping',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупки'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_unique'
            )
        ]
