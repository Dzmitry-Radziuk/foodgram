from core.constants import ADMIN_EXTRA
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Subscription, User


class SubscriptionInline(admin.TabularInline):
    """Отображает подписки пользователя в админке."""
    model = Subscription
    fk_name = 'user'
    extra = ADMIN_EXTRA
    verbose_name = 'Подписка'
    verbose_name_plural = 'Подписки'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для модели пользователя с подписками."""

    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_active', 'date_joined'
    )
    list_filter = ('is_staff', 'is_active')
    ordering = ('username',)
    list_display_links = ('username', 'email')
    inlines = [SubscriptionInline]
