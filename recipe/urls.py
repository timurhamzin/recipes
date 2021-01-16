from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import FollowRecipeView, FollowUserView


urlpatterns = [
    path('', views.index, name='index'),
    path('favorite_list/', views.favorite_list, name='favorite_list'),
    path('<int:recipe_id>/', views.single_page, name='single_page'),
    path('create/', views.create_recipe, name='create_recipe'),
    path('<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),
    path('shopping_cart/', views.shopping_cart, name='shopping_cart'),
    path('purchases/', views.ShoppingCartView.as_view()),
    path('purchases/<int:followed_id>/', views.ShoppingCartView.as_view()),
    path('subscriptions/', FollowUserView.as_view()),
    path('subscriptions/<int:followed_id>/', FollowUserView.as_view()),
    path('my_followed/', views.my_followed, name='my_followed'),
    path('author/<int:author_id>/', views.author, name='author'),
    path('favorites/', FollowRecipeView.as_view()),
    path('favorites/<int:followed_id>/', FollowRecipeView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
