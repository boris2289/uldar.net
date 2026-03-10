from django.urls import path

from .api_views import (
    ChangePasswordView,
    ListUserView,
    LoginView,
    RefreshTokenView,
    RegisterView,
    RetrieveUserView,
    UserMeView,
)


urlpatterns = [
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("users/", ListUserView.as_view(), name="user-list"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", UserMeView.as_view(), name="me"),
    path("me/change_password/", ChangePasswordView.as_view(), name="change-password"),
    path("users/<int:pk>/", RetrieveUserView.as_view(), name="user-retrieve"),
]