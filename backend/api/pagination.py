from core.constants import PAGE_SIZE
from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Кастомный пагинатор с требуемыми документацией лимитами."""

    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
