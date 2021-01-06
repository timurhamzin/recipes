from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
# from rest_framework.routers import DefaultRouter

from . import views
# from .views import FollowRecipeViewSet

# router = DefaultRouter()

urlpatterns = [
    path('', views.index, name='index'),
    path('favorites/', views.favorites, name='favorites'),
    path('<int:recipe_id>/', views.single_page, name='single_page'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# router.register(r'favorites/', FollowRecipeViewSet, basename='favorites')
