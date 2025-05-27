from core import constants
from django.contrib import admin
from django.db.models import Count

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    """Inline-админ для модели RecipeIngredient."""

    model = RecipeIngredient
    extra = constants.ADMIN_EXTRA
    min_num = constants.ADMIN_MIN_NUM
    verbose_name = 'Ингредиент в рецепте'
    verbose_name_plural = 'Ингредиенты в рецепте'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-класс для модели Recipe."""

    list_display = (
        'name',
        'author',
        'favorites_count',
        'shopping_cart_count',
        'created_at',
    )
    search_fields = (
        'name',
        'author__username',
        'author__first_name',
        'author__last_name',
    )
    list_filter = (
        'tags',
        'author',
        'created_at',
    )
    ordering = ('-created_at',)
    inlines = [RecipeIngredientInline]
    list_per_page = constants.LIST_PER_PAGE

    def get_queryset(self, request):
        """Возвращает расширенный queryset с аннотациями."""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'author').prefetch_related('tags').annotate(
            favorited_by_count=Count('favorites', distinct=True),
            in_shopping_cart_count=Count('shopping_carts', distinct=True),
        )

    @admin.display(
        description='Добавлено в избранное',
        ordering='favorited_by_count',
    )
    def favorites_count(self, obj):
        """Количество пользователей, добавивших рецепт в избранное."""
        return obj.favorited_by_count

    @admin.display(
        description='Добавлено в корзину',
        ordering='in_shopping_cart_count',
    )
    def shopping_cart_count(self, obj):
        """Количество пользователей, добавивших рецепт в корзину."""
        return obj.in_shopping_cart_count


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-класс для модели Ingredient."""

    search_fields = ('name',)
    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    ordering = ('name',)
    list_per_page = constants.LIST_PER_PAGE


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-класс для модели Tag."""

    search_fields = ('name', 'slug')
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
