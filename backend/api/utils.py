import io
import random
import string

from core.constants import BUFFER_VALUE, LENGHT_SHORT_CODE
from rest_framework import status
from rest_framework.response import Response


def generate_short_code(length=LENGHT_SHORT_CODE):
    """Генерирует код рецепта."""
    return ''.join(random.choices(
        string.ascii_letters + string.digits, k=length))


def handle_post_delete(request, model_class, serializer_class, recipe):
    """Обрабатывает добавление или удаление рецепта из связанной модели."""
    user = request.user

    if request.method == 'POST':
        serializer = serializer_class(
            data={'recipe': recipe.id, 'user': user.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    deleted, _ = model_class.objects.filter(user=user, recipe=recipe).delete()
    if deleted:
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'detail': 'Запись не найдена'}, status=status.HTTP_400_BAD_REQUEST)


def prepare_buffer(content):
    """Создает и подготавливает буфер для чтения с содержимым content."""
    buffer = io.BytesIO()
    buffer.write(content.encode('utf-8'))
    buffer.seek(BUFFER_VALUE)
    return buffer
