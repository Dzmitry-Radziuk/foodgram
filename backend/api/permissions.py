from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает редактирование объекта только его автору.

    - Чтение (GET, HEAD, OPTIONS) доступно всем.
    - Изменение (PUT, PATCH, DELETE) — только если пользователь
    является автором объекта.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
