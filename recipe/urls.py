from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
from .views import FollowRecipeView, FollowUserView

urlpatterns = [
    path('', views.index, name='index'),
    path('favorite_list/', views.favorite_list, name='favorite_list'),
    path('<int:recipe_id>/', views.single_page, name='single_page'),
    path('create/', views.create_recipe, name='create_recipe'),
    path('<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),
    path('purchases/', views.ShoppingCartView.as_view()),
    path('purchases/<int:followed_id>/', views.ShoppingCartView.as_view()),
    path('subscriptions/', FollowUserView.as_view()),
    path('subscriptions/<int:followed_id>/', FollowUserView.as_view()),
    path('favorites/', FollowRecipeView.as_view()),
    path('favorites/<int:followed_id>/', FollowRecipeView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# router.register(r'change/', RecipeViewSet, basename='change')
# path('<int:recipe_id>/edit_model_form/', views.edit_model_form,
#      name='edit_model_form'),
