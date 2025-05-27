from core import constants
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.text import Truncator


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Атрибуты:
        email (EmailField): Уникальный email пользователя.
        username (CharField): Уникальное имя пользователя.
        first_name (CharField): Имя пользователя.
        last_name (CharField): Фамилия пользователя.
        avatar (ImageField): Аватар пользователя (необязательно).
    """

    email = models.EmailField(
        unique=True,
        verbose_name='Почта',
        help_text='Введите уникальный адрес электронной почты'
    )
    username = models.CharField(
        max_length=constants.MAX_LENGTH_USERNAME,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        verbose_name='Имя пользователя',
        help_text='Введите ваш никнейм',
    )
    first_name = models.CharField(
        max_length=constants.MAX_LENGTH_FIRST_NAME,
        verbose_name='Имя',
        help_text='Введите ваше имя',
    )
    last_name = models.CharField(
        max_length=constants.MAX_LENGTH_LAST_NAME,
        verbose_name='Фамилия',
        help_text='Введите вашу фамилию',
    )
    avatar = models.ImageField(
        upload_to='images/avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар',
        help_text='Загрузите изображение аватара (необязательно)',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name'
    ]

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Возвращает укороченное имя пользователя."""
        return Truncator(self.username).chars(constants.MAX_LENGTH_STR)


class Subscription(models.Model):
    """Модель подписок пользователя на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
        help_text='Пользователь, который подписывается'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
        help_text='Автор, на которого подписываются'
    )

    class Meta:
        ordering = ['user__username']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        """Возвращает строку вида 'user подписан на author'."""
        user = Truncator(
            str(self.user)).chars(constants.MAX_LENGTH_STR)
        author = Truncator(
            str(self.author)).chars(constants.MAX_LENGTH_STR)
        return f'{user} подписан на {author}'
