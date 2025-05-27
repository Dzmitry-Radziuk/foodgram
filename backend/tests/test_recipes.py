import base64
from io import BytesIO

import pytest
from PIL import Image
from rest_framework import status


RECIPES_URL = '/api/recipes/'


def create_test_image_bytes():
    """Создаёт PNG изображение размером 1x1 пиксель и возвращает его байты."""
    buffer = BytesIO()
    image = Image.new('RGBA', (1, 1), (255, 0, 0, 0))
    image.save(buffer, format='PNG')
    return buffer.getvalue()


def get_base64_image_string():
    """
    Возвращает изображение в виде строки base64,
    подходящей для поля image.
    """
    image_data = create_test_image_bytes()
    return f'data:image/png;base64,{base64.b64encode(image_data).decode()}'


@pytest.mark.django_db
def test_list_recipes(
    api_client,
    recipe_factory
):
    """Проверяет успешное получение списка рецептов."""
    recipe_factory(name='Рецепт 1')
    recipe_factory(name='Рецепт 2')

    response = api_client.get(RECIPES_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) >= 2


@pytest.mark.django_db
def test_retrieve_recipe(
    api_client,
    recipe_factory
):
    """Проверяет получение данных конкретного рецепта по его ID."""
    recipe = recipe_factory(name='Уникальный рецепт')

    response = api_client.get(f'{RECIPES_URL}{recipe.id}/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Уникальный рецепт'


@pytest.mark.django_db
def test_create_recipe_authenticated(
    api_client,
    user_factory,
    tag_factory,
    ingredient_factory
):
    """
    Проверяет, что аутентифицированный пользователь
    может создать рецепт с изображением.
    """
    user = user_factory()
    tag = tag_factory()
    ingredient = ingredient_factory()
    api_client.force_authenticate(user=user)

    data = {
        'name': 'Суп из картошки',
        'text': 'Варить 30 минут',
        'cooking_time': 30,
        'tags': [tag.id],
        'ingredients': [{'id': ingredient.id, 'amount': 3}],
        'image': get_base64_image_string(),
    }

    response = api_client.post(RECIPES_URL, data=data, format='json')

    print('Status code:', response.status_code)
    print('Response data:', response.data)

    assert response.status_code == 201


@pytest.mark.django_db
def test_create_recipe_unauthenticated(
    api_client,
    tag_factory,
    ingredient_factory
):
    """
    Проверяет, что неаутентифицированный пользователь
    не может создать рецепт.
    """
    tag = tag_factory()
    ingredient = ingredient_factory()

    payload = {
        'name': 'Запрещённый суп',
        'text': 'Нельзя без логина',
        'cooking_time': 15,
        'tags': [tag.id],
        'ingredients': [{'id': ingredient.id, 'amount': 2}],
    }

    response = api_client.post(RECIPES_URL, payload, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_recipe_by_multiple_users(
    api_client,
    user_factory,
    tag_factory,
    ingredient_factory
):
    """
    Создаёт нескольких пользователей с разными правами
    и проверяет, что каждый может создать свой рецепт.
    """
    tag = tag_factory()
    ingredient = ingredient_factory()

    users = [
        user_factory(is_staff=False, is_superuser=False),
        user_factory(is_staff=True, is_superuser=False),
        user_factory(is_staff=True, is_superuser=True),
    ]

    for user in users:
        api_client.force_authenticate(user=user)

        data = {
            'name': f'Рецепт пользователя {user.username}',
            'text': 'Тестовый рецепт',
            'cooking_time': 20,
            'tags': [tag.id],
            'ingredients': [{'id': ingredient.id, 'amount': 2}],
            'image': get_base64_image_string(),
        }

        response = api_client.post(RECIPES_URL, data=data, format='json')
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_recipe_without_ingredients_returns_400(
    api_client,
    user_factory,
    tag_factory
):
    """Проверяет, что рецепт без ингредиентов не создаётся."""
    user = user_factory()
    tag = tag_factory()
    api_client.force_authenticate(user=user)

    data = {
        'name': 'Без ингредиентов',
        'text': 'Нельзя так',
        'cooking_time': 15,
        'tags': [tag.id],
        'ingredients': [],
        'image': get_base64_image_string(),
    }

    response = api_client.post(RECIPES_URL, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'ingredients' in response.data


@pytest.mark.django_db
def test_create_recipe_with_duplicate_ingredients_returns_400(
    api_client,
    user_factory,
    tag_factory,
    ingredient_factory
):
    """Проверяет, что нельзя добавить повторяющиеся ингредиенты."""
    user = user_factory()
    tag = tag_factory()
    ingredient = ingredient_factory()
    api_client.force_authenticate(user=user)

    data = {
        'name': 'Повтор ингредиентов',
        'text': 'Ошибка должна быть',
        'cooking_time': 20,
        'tags': [tag.id],
        'ingredients': [
            {'id': ingredient.id, 'amount': 1},
            {'id': ingredient.id, 'amount': 2}
        ],
        'image': get_base64_image_string(),
    }

    response = api_client.post(RECIPES_URL, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Ингредиенты не должны повторяться' in str(response.data)


@pytest.mark.django_db
def test_create_recipe_without_tags_returns_400(
    api_client,
    user_factory,
    ingredient_factory
):
    """Проверяет, что рецепт без тегов не создаётся."""
    user = user_factory()
    ingredient = ingredient_factory()
    api_client.force_authenticate(user=user)

    data = {
        'name': 'Без тегов',
        'text': 'Это неправильно',
        'cooking_time': 10,
        'tags': [],
        'ingredients': [{'id': ingredient.id, 'amount': 1}],
        'image': get_base64_image_string(),
    }

    response = api_client.post(RECIPES_URL, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'tags' in response.data


@pytest.mark.django_db
def test_create_recipe_with_duplicate_tags_returns_400(
    api_client,
    user_factory,
    tag_factory,
    ingredient_factory
):
    """Проверяет, что нельзя добавить одинаковые теги дважды."""
    user = user_factory()
    tag = tag_factory()
    ingredient = ingredient_factory()
    api_client.force_authenticate(user=user)

    data = {
        'name': 'Повтор тегов',
        'text': 'Ошибка ожидается',
        'cooking_time': 25,
        'tags': [tag.id, tag.id],
        'ingredients': [{'id': ingredient.id, 'amount': 1}],
        'image': get_base64_image_string(),
    }

    response = api_client.post(RECIPES_URL, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Теги не должны повторяться' in str(response.data)


@pytest.mark.django_db
def test_create_recipe_with_invalid_cooking_time_returns_400(
    api_client,
    user_factory,
    tag_factory,
    ingredient_factory
):
    """Проверяет, что рецепт с нулевым или отр-ым временем не создаётся."""
    user = user_factory()
    tag = tag_factory()
    ingredient = ingredient_factory()
    api_client.force_authenticate(user=user)

    for invalid_time in [0, -5]:
        data = {
            'name': 'Неверное время',
            'text': 'Ошибка по времени',
            'cooking_time': invalid_time,
            'tags': [tag.id],
            'ingredients': [{'id': ingredient.id, 'amount': 1}],
            'image': get_base64_image_string(),
        }

        response = api_client.post(RECIPES_URL, data=data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Время приготовления должно быть не менее одной минуты' in str(
            response.data)
