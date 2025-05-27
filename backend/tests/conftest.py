import itertools

import pytest
from rest_framework.test import APIClient

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


_user_counter = itertools.count()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    """Обычный пользователь."""
    return User.objects.create_user(
        username='user', email='user@test.com', password='1234')


@pytest.fixture
def admin_user(db):
    """Администратор."""
    return User.objects.create_superuser(
        username='admin', email='admin@test.com', password='adminpass')


@pytest.fixture
def user_factory(db):
    """Фабрика пользователей."""
    def create_user(**kwargs):
        uid = next(_user_counter)
        defaults = {
            'username': f'testuser_{uid}',
            'email': f'user{uid}@test.com',
            'password': '1234'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return create_user


@pytest.fixture
def ingredient_factory(db):
    """Фабрика ингредиентов."""
    def create_ingredient(**kwargs):
        defaults = {'name': 'Tomato', 'measurement_unit': 'pcs'}
        defaults.update(kwargs)
        return Ingredient.objects.create(**defaults)
    return create_ingredient


@pytest.fixture
def tag_factory(db):
    """Фабрика тегов."""
    def create_tag(**kwargs):
        defaults = {'name': 'Breakfast', 'slug': 'breakfast'}
        defaults.update(kwargs)
        return Tag.objects.create(**defaults)
    return create_tag


@pytest.fixture
def recipe_factory(db, user_factory):
    """Фабрика рецептов от разных пользователей."""
    def create_recipe(author=None, **kwargs):
        if not author:
            author = user_factory()
        defaults = {
            'author': author,
            'name': 'Test Recipe',
            'text': 'Test description',
            'cooking_time': 10,
        }
        defaults.update(kwargs)
        return Recipe.objects.create(**defaults)
    return create_recipe


@pytest.fixture
def multiple_users_with_recipes(db, user_factory, recipe_factory):
    """Создает нескольких пользователей и рецепты от каждого."""
    users = [user_factory(username=f'user{i}') for i in range(3)]
    recipes = []
    for user in users:
        recipes.append(recipe_factory(
            author=user, name=f'Рецепт от {user.username}'))
    return {'users': users, 'recipes': recipes}
