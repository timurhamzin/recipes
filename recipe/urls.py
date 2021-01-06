from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import RecipeViewSet

router = DefaultRouter()
from .views import FavoriteRecipe

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:recipe_id>/', views.single_page, name='single_page'),
    path('<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('favorites/', FavoriteRecipe.as_view()),
    path('favorites/<int:recipe_id>/', FavoriteRecipe.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# router.register(r'change/', RecipeViewSet, basename='change')
