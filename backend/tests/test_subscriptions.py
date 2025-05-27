import pytest
from rest_framework import status

from users.models import Subscription


SUBSCRIBE_URL = '/api/users/{id}/subscribe/'
SUBSCRIPTIONS_LIST_URL = '/api/users/subscriptions/'


@pytest.mark.django_db
def test_user_can_subscribe(
    api_client,
    user_factory
):
    """
    Проверяет, что авторизованный пользователь
    может подписаться на другого пользователя.
    """
    user = user_factory()
    author = user_factory()
    api_client.force_authenticate(user=user)

    response = api_client.post(SUBSCRIBE_URL.format(id=author.id))

    assert response.status_code == status.HTTP_201_CREATED
    assert Subscription.objects.filter(user=user, author=author).exists()


@pytest.mark.django_db
def test_user_cannot_subscribe_twice(
    api_client,
    user_factory
):
    """
    Проверяет, что нельзя подписаться дважды
    на одного и того же автора.
    """
    user = user_factory()
    author = user_factory()
    api_client.force_authenticate(user=user)
    api_client.post(SUBSCRIBE_URL.format(id=author.id))
    response = api_client.post(SUBSCRIBE_URL.format(id=author.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_cannot_subscribe_to_self(
    api_client,
    user_factory
):
    """Проверяет, что пользователь не может подписаться сам на себя."""
    user = user_factory()
    api_client.force_authenticate(user=user)

    response = api_client.post(SUBSCRIBE_URL.format(id=user.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_can_unsubscribe(
    api_client,
    user_factory
):
    """
    Проверяет, что пользователь может отписаться
    от другого пользователя.
    """
    user = user_factory()
    author = user_factory()
    api_client.force_authenticate(user=user)

    api_client.post(SUBSCRIBE_URL.format(id=author.id))
    response = api_client.delete(SUBSCRIBE_URL.format(id=author.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Subscription.objects.filter(user=user, author=author).exists()


@pytest.mark.django_db
def test_view_subscription_list(
    api_client,
    user_factory
):
    """Проверяет, что список подписок пользователя отображается корректно."""
    user = user_factory()
    author1 = user_factory()
    author2 = user_factory()
    api_client.force_authenticate(user=user)

    api_client.post(SUBSCRIBE_URL.format(id=author1.id))
    api_client.post(SUBSCRIBE_URL.format(id=author2.id))

    response = api_client.get(SUBSCRIPTIONS_LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2
