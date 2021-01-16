"""recipes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

from recipes import views

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('', include('recipe.urls')),
]

urlpatterns += staticfiles_urlpatterns()

urlpatterns += [
    path('register/', views.register, name='register'),

    path('auth/', views.auth, name='auth'),
    path('signout/', views.signout, name='signout'),

    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='changePassword.html'), name='password_change'),
    path('password_change/done/', views.password_change_done,
         name='password_change_done'),

    path('reset_password/', auth_views.PasswordResetView.as_view(
             template_name='resetPassword.html'),
         name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
