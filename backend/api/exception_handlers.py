from http import HTTPStatus

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Обрабатывает исключения в DRF с пользовательским сообщением."""
    response = exception_handler(exc, context)

    if response is not None and response.status_code == HTTPStatus.NOT_FOUND:
        response.data = {'detail': 'Страница не найдена.'}

    return response
