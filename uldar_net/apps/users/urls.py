from django.contrib import admin
from django.urls import path
from .api_views import RegisterView, UserMeView, ChangePasswordView, ListUserView, RetrieveUserView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)


urlpatterns = [

    path('login/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('users/', ListUserView.as_view(), name='list'),
    path('register/', RegisterView.as_view(), name="register"),
    path('me/', UserMeView.as_view(), name="me"),
    path('me/change_password/', ChangePasswordView.as_view(), name="change-password"),
    path('users/<int:pk>', RetrieveUserView.as_view(), name='retrieve')


]

