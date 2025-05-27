import pytest
from rest_framework import status

from recipes.models import Favorite


FAVORITE_URL = '/api/recipes/{id}/favorite/'


@pytest.mark.django_db
def test_add_to_favorites(
    api_client,
    user_factory,
    recipe_factory
):
    """
    Проверяет, что авторизованный
    пользователь может добавить рецепт в избранное.
    """
    user = user_factory()
    recipe = recipe_factory(author=user)
    api_client.force_authenticate(user=user)

    response = api_client.post(FAVORITE_URL.format(id=recipe.id))

    assert response.status_code == status.HTTP_201_CREATED
    assert Favorite.objects.filter(user=user, recipe=recipe).exists()


@pytest.mark.django_db
def test_add_duplicate_favorite(
    api_client,
    user_factory,
    recipe_factory
):
    """
    Проверяет, что повторное добавление
    одного и того же рецепта в избранное не допускается.
    """
    user = user_factory()
    recipe = recipe_factory(author=user)
    api_client.force_authenticate(user=user)

    api_client.post(FAVORITE_URL.format(id=recipe.id))
    response = api_client.post(FAVORITE_URL.format(id=recipe.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Favorite.objects.filter(user=user, recipe=recipe).count() == 1


@pytest.mark.django_db
def test_remove_from_favorites(
    api_client,
    user_factory,
    recipe_factory
):
    """
    Проверяет, что авторизованный
    пользователь может удалить рецепт из избранного.
    """
    user = user_factory()
    recipe = recipe_factory(author=user)
    Favorite.objects.create(user=user, recipe=recipe)
    api_client.force_authenticate(user=user)

    response = api_client.delete(FAVORITE_URL.format(id=recipe.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Favorite.objects.filter(user=user, recipe=recipe).exists()


@pytest.mark.django_db
def test_unauthenticated_cannot_add_favorite(
    api_client,
    recipe_factory,
    user_factory
):
    """
    Проверяет, что неавторизованный
    пользователь не может добавить рецепт в избранное.
    """
    recipe = recipe_factory(author=user_factory())
    response = api_client.post(FAVORITE_URL.format(id=recipe.id))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
