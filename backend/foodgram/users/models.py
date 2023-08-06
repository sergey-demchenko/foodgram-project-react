from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    """ Модель пользователя. """

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=30,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=30
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=100,
        unique=True
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=30,
        unique=True,
        validators=[UnicodeUsernameValidator(
            message='Имя не соответсвует стандарту Unicode'
        )]
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name'
    ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """ Модель подписки. """

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='subscriber',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='author',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='subscription_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
