from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    ChangePasswordResponseSerializer,
    ChangePasswordSerializer,
    ListUserSerializer,
    LoginRequestSerializer,
    RegisterSerializer,
    RetrieveUserSerializer,
    TokenPairResponseSerializer,
    TokenRefreshRequestSerializer,
    TokenRefreshResponseSerializer,
    UserSerializer,
)


User = get_user_model()


@extend_schema(
    tags=["Users"],
    summary="Register a user",
    request=RegisterSerializer,
    responses={201: UserSerializer},
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=HTTP_201_CREATED)


@extend_schema(
    tags=["Users"],
    summary="Get current user",
    responses={200: UserSerializer},
)
class UserMeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(
    tags=["Users"],
    summary="Change current user password",
    request=ChangePasswordSerializer,
    responses={200: ChangePasswordResponseSerializer},
)
class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": ["Wrong password."]}, status=HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"status": "password changed"}, status=HTTP_200_OK)


@extend_schema(
    tags=["Users"],
    summary="List users",
    responses={200: ListUserSerializer(many=True)},
)
class ListUserView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=["Users"],
    summary="Retrieve user by id",
    responses={200: RetrieveUserSerializer},
)
class RetrieveUserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = RetrieveUserSerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=["Auth"],
    summary="Login and get JWT tokens",
    request=LoginRequestSerializer,
    responses={200: TokenPairResponseSerializer},
)
class LoginView(TokenObtainPairView):
    pass


@extend_schema(
    tags=["Auth"],
    summary="Refresh access token",
    request=TokenRefreshRequestSerializer,
    responses={200: TokenRefreshResponseSerializer},
)
class RefreshTokenView(TokenRefreshView):
    pass