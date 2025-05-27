import os

from core import constants
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import Truncator

from api.utils import generate_short_code


User = get_user_model()


class Tag(models.Model):
    """Модель Тега для классификации рецептов."""

    name = models.CharField(
        max_length=constants.MAX_LENGTH_NAME_TAG,
        unique=True,
        verbose_name='Название тега',
        help_text=('Введите уникальное название тега'
                   '(например, "Завтрак", "Веган")')
    )
    slug = models.SlugField(
        max_length=constants.MAX_LENGTH_SLUG_TAG,
        unique=True,
        verbose_name='Слаг',
        help_text=('Введите уникальный слаг тега (только латиница,'
                   'цифры и дефисы), например "breakfast"')
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return Truncator(self.name).chars(constants.MAX_LENGTH_STR)


class Ingredient(models.Model):
    """Модель ингредиента для рецептов."""

    name = models.CharField(
        max_length=constants.MAX_LENGTH_NAME_INGREDIENT,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента (например, "Сахар", "Молоко")'
    )
    measurement_unit = models.CharField(
        max_length=constants.MAX_LENGTH_MEASUREMENT_UNIT,
        verbose_name='Единица измерения',
        help_text=('Укажите единицу измерения ингредиента'
                   '(например, г, мл, ст. л.)')
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        name = Truncator(self.name).chars(constants.MAX_LENGTH_STR)
        measurement_unit = Truncator(
            self.measurement_unit).chars(
                constants.MAX_LENGTH_STR_MEASUREMENT_UNIT)
        return f'{name}, {measurement_unit}'


class Recipe(models.Model):
    """
    Модель рецепта.

    Атрибуты:
        author (ForeignKey): Автор рецепта (пользователь).
        name (CharField): Название рецепта.
        text (TextField): Описание рецепта.
        cooking_time (PositiveSmallIntegerField): Время приготовления в мин.
        image (ImageField): Изображение блюда.
        tags (ManyToManyField): Теги, связанные с рецептом.
        ingredients (ManyToManyField): Ингредиенты рецепта
        через промежуточную модель.
        short_code (CharField): Короткая уникальная ссылка на рецепт.
        created_at (DateTimeField): Дата и время создания рецепта.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        help_text='Пользователь, создавший рецепт'
    )
    name = models.CharField(
        max_length=constants.MAX_LENGTH_NAME_RECIPE,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Полное описание рецепта, включая способ приготовления'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(constants.MIN_COOKING_TIME)],
        verbose_name='Время приготовления (в минутах)',
        help_text=(f'Введите время приготовления в минутах'
                   f'(минимум {constants.MIN_COOKING_TIME} мин)')
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение рецепта',
        help_text='Загрузите изображение готового блюда'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Выберите теги, которые описывают рецепт'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Добавьте ингредиенты и их количество'
    )
    short_code = models.CharField(
        max_length=constants.MAX_LENGTH_SHORT_CODE,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Короткая ссылка',
        help_text=('Уникальный короткий код для рецепта,'
                   'генерируется автоматически')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        help_text='Дата и время создания рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']
        default_related_name = 'recipes'

    def __str__(self):
        name = Truncator(self.name).chars(constants.MAX_LENGTH_STR)
        return f'{name}'

    def save(self, *args, **kwargs):
        """Генерация короткого кода, если он не задан."""
        if not self.short_code:
            while True:
                code = generate_short_code()
                if not Recipe.objects.filter(short_code=code).exists():
                    self.short_code = code
                    break
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Удаляет изображение из файловой системы при удалении рецепта."""
        if self.image:
            image_path = self.image.path
            if os.path.isfile(image_path):
                os.remove(image_path)
        super().delete(*args, **kwargs)


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи рецептов и ингредиентов + количество."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт, к которому относится ингредиент'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        help_text='Ингредиент рецепта'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(constants.MIN_AMOUNT)],
        verbose_name='Количество',
        help_text=f'Количество ингредиента (минимум {constants.MIN_AMOUNT})'
    )

    class Meta:
        ordering = ['ingredient__name']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        default_related_name = 'recipe_ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        ingredient = Truncator(self.ingredient).chars(
            constants.MAX_LENGTH_STR)
        amount = Truncator(self.amount).chars(constants.MAX_LENGTH_STR)
        return f'{ingredient} — {amount}'


class Favorite(models.Model):
    """Модель избранных рецептов пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Пользователь, добавивший рецепт в избранное'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        help_text='Рецепт, добавленный в избранное'
    )

    class Meta:
        ordering = ['user__username']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        user = Truncator(self.user).chars(constants.MAX_LENGTH_STR)
        recipe = Truncator(self.recipe).chars(constants.MAX_LENGTH_STR)
        return f'{user} добавил {recipe} в избранное'


class ShoppingCart(models.Model):
    """Модель корзины покупок пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Пользователь, добавивший рецепт в корзину покупок'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в корзине',
        help_text='Рецепт, добавленный в корзину покупок'
    )

    class Meta:
        ordering = ['recipe__name']
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        default_related_name = 'shopping_carts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        user = Truncator(self.user).chars(constants.MAX_LENGTH_STR)
        recipe = Truncator(self.recipe).chars(constants.MAX_LENGTH_STR)
        return f'{user} добавил {recipe} в избранное'
