from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    
]
