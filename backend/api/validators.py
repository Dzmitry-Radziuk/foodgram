from core.constants import MIN_COOKING_TIME
from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Favorite, ShoppingCart


User = get_user_model()


def validate_subscription(user, author):
    """Проверка невозможности подписки на самого себя и повторной подписки."""
    if user == author:
        raise serializers.ValidationError(
            'Нельзя подписаться на самого себя.')
    if author.subscribers.filter(user=user).exists():
        raise serializers.ValidationError(
            'Вы уже подписаны на этого пользователя.')


def validate_avatar_required_for_put(value, context):
    """Проверка обязательности поля avatar при PUT-запросе."""
    request = context.get('request')
    if request and request.method == 'PUT' and not value:
        raise serializers.ValidationError(
            {'avatar': 'Обязательное поле.'})


def validate_cooking_time(value):
    """Проверка минимального времени приготовления."""
    if value < MIN_COOKING_TIME:
        raise serializers.ValidationError(
            "Время приготовления должно быть не менее одной минуты.")
    return value


def validate_ingredients(ingredients):
    """Проверка наличия и уникальности ингредиентов."""
    if not ingredients:
        raise serializers.ValidationError({
            'ingredients': 'Необходимо указать хотя бы один ингредиент.'
        })
    ingredient_ids = (item['id'] for item in ingredients)
    ingredient_ids_list = list(ingredient_ids)
    if len(ingredient_ids_list) != len(set(ingredient_ids_list)):
        raise serializers.ValidationError({
            'ingredients': 'Ингредиенты не должны повторяться.'
        })
    return ingredients


def validate_tags(tags):
    """Проверка уникальности тегов."""
    if len(tags) != len(set(tags)):
        raise serializers.ValidationError({
            'tags': 'Теги не должны повторяться.'
        })
    return tags


def validate_recipe_fields(attrs):
    """Валидирует обязательные поля рецепта."""
    if not attrs.get('ingredients'):
        raise serializers.ValidationError(
            {'ingredients': 'Обязательное поле.'})
    if not attrs.get('tags'):
        raise serializers.ValidationError(
            {'tags': 'Обязательное поле.'})
    validate_ingredients(attrs['ingredients'])
    validate_tags(attrs['tags'])
    return attrs


def validate_unique_favorite(user, recipe):
    """Проверка наличия рецепта в избранном пользователя."""
    if Favorite.objects.filter(user=user, recipe=recipe).exists():
        raise serializers.ValidationError('Рецепт уже в избранном')


def validate_unique_shopping_cart(user, recipe):
    """Проверка наличия рецепта в корзине пользователя."""
    if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
        raise serializers.ValidationError('Рецепт уже в списке покупок')
