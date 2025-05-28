from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets

from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from django.http import HttpResponseNotFound
from rest_framework.response import Response
from django.views import View
from api import serializers
from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.utils import handle_post_delete, prepare_buffer
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""

    serializer_class = serializers.UserSerializer
    lookup_field = 'pk'
    filter_backends = (SearchFilter,)
    search_fields = ['username', 'email']
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        """Возвращает queryset пользователей с предзагрузкой подписок."""
        return User.objects.prefetch_related('subscriptions').all()

    def get_serializer_class(self):
        """Определяет класс сериализатора."""
        if self.action == 'avatar' and self.request.method == 'PUT':
            return serializers.UserAvatarSerializer
        if self.action in ['list', 'retrieve', 'me']:
            return serializers.UserSerializer
        if self.action == 'subscribe':
            return serializers.SubscriptionSerializer
        if self.action == 'subscriptions':
            return serializers.SubscribedUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        """Возвращает список классов разрешений в зависимости от действия."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action in ['me', 'subscriptions', 'subscribe', 'avatar']:
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        """Обработка PUT-запроса для обновления аватара и DELETE-запроса."""
        user = request.user

        if request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Аватар не найден'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        """Подписка (POST) или отписка (DELETE) текущего пользователя."""
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            serializer = self.get_serializer(
                data={'user': user.id, 'author': author.id},
                context={'request': request, 'view': self}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = Subscription.objects.filter(
            user=user, author=author
        ).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'detail': 'Вы не подписаны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        """Возвращает список подписок текущего пользователя с пагинацией."""
        user = request.user
        authors = User.objects.filter(
            subscribers__user=user).order_by('-id')
        paginated_authors = self.paginate_queryset(authors)
        serializer = self.get_serializer(
            paginated_authors, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class ShortLinkRedirectView(View):
    """Редирект на страницу рецепта по короткой ссылке."""

    def get(self, request, short_code):
        try:
            recipe = Recipe.objects.get(short_code=short_code)
        except Recipe.DoesNotExist:
            return HttpResponseNotFound('Рецепт не существует!')

        frontend_base_url = request.scheme + '://' + request.get_host()

        redirect_url = f'{frontend_base_url}/recipes/{recipe.id}/'
        return redirect(redirect_url)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для CRUD операций с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination
    search_fields = ['name']
    ordering_fields = ['name', 'author', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Выбор сериализатора для чтения или записи."""
        if self.request.method == 'GET':
            return serializers.RecipeReadSerializer
        return serializers.RecipeWriteSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        recipe = self.get_object()
        short_url = request.build_absolute_uri(
            reverse('short-link', args=[recipe.short_code])
        )
        return Response({'short-link': short_url})

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта из избранного."""
        recipe = self.get_object()
        return handle_post_delete(
            request, Favorite, serializers.FavoriteSerializer, recipe
        )

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта из корзины покупок."""
        recipe = self.get_object()
        return handle_post_delete(
            request, ShoppingCart, serializers.ShoppingCartSerializer, recipe
        )

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивает список покупок в текстовом файле."""
        user = request.user
        ingredients = self.get_shopping_cart_ingredients(user)
        content = self.format_shopping_list_text(ingredients)
        return self.create_text_file_response(
            content, filename="shopping_cart.txt"
        )

    def get_shopping_cart_ingredients(self, user):
        """Получить ингредиенты из корзины пользователя с суммированием."""
        return (
            RecipeIngredient.objects
            .filter(recipe__shopping_carts__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )

    def format_shopping_list_text(self, ingredients):
        """Форматирует список ингредиентов в текст для скачивания."""
        lines = ['Список покупок:\n']
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            amount = item['amount']
            lines.append(f'{name} ({unit}) — {amount}')
        return '\n'.join(lines)

    def create_text_file_response(self, content, filename):
        """Создаёт HTTP-ответ с текстовым файлом для скачивания."""
        buffer = prepare_buffer(content)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename,
            content_type='text/plain; charset=utf-8',
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для чтения тегов рецептов."""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для чтения ингредиентов с фильтрацией по имени."""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
