from http import HTTPStatus

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Обрабатывает исключения в DRF с пользовательским сообщением.

    Заменяет стандартное сообщение об ошибке 404 на пользовательское —
    'Страница не найдена.' Остальные ошибки обрабатываются стандартным
    обработчиком DRF.

    Args:
        exc: Исключение, вызванное во время запроса.
        context: Словарь с контекстом запроса (например, view).

    Returns:
        Response: Объект ответа DRF с переопределённым сообщением,
        если ошибка — 404. В остальных случаях — стандартный ответ DRF.
    """
    response = exception_handler(exc, context)

    if response is not None and response.status_code == HTTPStatus.NOT_FOUND:
        response.data = {'detail': 'Страница не найдена.'}

    return response
