import pytest
from rest_framework import status

from users.models import User


USERS_URL = '/api/users/'
ME_URL = '/api/users/me/'
SET_PASSWORD_URL = '/api/users/set_password/'
TOKEN_LOGOUT_URL = '/api/auth/token/logout/'
TOKEN_LOGIN_URL = '/api/auth/token/login/'
TOKEN_LOGOUT_URL = '/api/auth/token/logout/'


@pytest.mark.django_db
def test_user_registration(
    api_client
):
    """Проверяет регистрацию пользователя через UserViewSet."""
    payload = {
        'email': 'newuser@example.com',
        'username': 'newuser',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'password': 'securepassword123'
    }
    response = api_client.post(USERS_URL, data=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
def test_user_login(
    api_client,
    user_factory
):
    """Проверяет аутентификацию пользователя через Djoser токены."""
    user = user_factory(password='pass1234')
    response = api_client.post(TOKEN_LOGIN_URL, data={
        'email': user.email,
        'password': 'pass1234'
    })
    assert response.status_code == status.HTTP_200_OK
    assert 'auth_token' in response.data


@pytest.mark.django_db
def test_get_current_user(
    api_client,
    user_factory
):
    """Проверяет получение данных текущего пользователя."""
    user = user_factory()
    api_client.force_authenticate(user=user)
    response = api_client.get(ME_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == user.email


@pytest.mark.django_db
def test_set_password(
    api_client,
    user_factory
):
    """Проверяет изменение пароля пользователя."""
    user = user_factory()
    api_client.force_authenticate(user=user)
    payload = {
        'current_password': '1234',
        'new_password': 'newsecurepass'
    }
    response = api_client.post(SET_PASSWORD_URL, data=payload)
    assert response.status_code in [
        status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]


@pytest.mark.django_db
def test_user_logout(
    api_client,
    user_factory
):
    """Проверяет логаут пользователя."""
    user = user_factory()
    api_client.force_authenticate(user=user)
    response = api_client.post(TOKEN_LOGOUT_URL)
    assert response.status_code == status.HTTP_204_NO_CONTENT
