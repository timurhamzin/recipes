from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
from .views import FavoriteRecipe

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:recipe_id>/', views.single_page, name='single_page'),
    path('<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),
    path('purchases/', views.Purchase.as_view()),
    path('purchases/<int:recipe_id>/', views.Purchase.as_view()),
    path('favorites/', FavoriteRecipe.as_view()),
    path('favorites/<int:recipe_id>/', FavoriteRecipe.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# router.register(r'change/', RecipeViewSet, basename='change')
# path('<int:recipe_id>/edit_model_form/', views.edit_model_form,
#      name='edit_model_form'),
