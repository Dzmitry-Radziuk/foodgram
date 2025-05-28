from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget

from recipes.models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    """
    Фильтры для модели Recipe.

    - фильтрация по автору,
    - фильтрация по тегам (slug),
    - фильтрация по признаку добавления в избранное,
    - фильтрация по признаку добавления в корзину.
    """

    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited',
        widget=BooleanWidget()
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart',
        widget=BooleanWidget()
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if user and value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if user and value and user.is_authenticated:
            return queryset.filter(shopping_carts__user=user)
        return queryset


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов по полю 'name' с учётом начала строки."""

    name = filters.CharFilter(
        field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
