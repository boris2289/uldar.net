from django.contrib.auth import get_user_model
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
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


ERROR_400_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "oneOf": [
            {"type": "array", "items": {"type": "string"}},
            {"type": "string"},
        ]
    },
    "example": {
        "email": ["This field is required."],
        "password": ["This password is too short."]
    },
}

ERROR_401_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {"type": "string", "example": "Authentication credentials were not provided."}
    },
}

ERROR_403_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {"type": "string", "example": "You do not have permission to perform this action."}
    },
}

ERROR_404_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {"type": "string", "example": "Not found."}
    },
}

ERROR_429_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {"type": "string", "example": "Request was throttled."}
    },
}


@extend_schema(
    tags=["Auth"],
    summary="Register a new user",
    description=(
        "Creates a new user account. Authentication is not required. "
        "The request body must contain the fields required by the registration serializer."
    ),
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(
            response=UserSerializer,
            description="User was created successfully.",
        ),
        400: OpenApiResponse(
            response=ERROR_400_SCHEMA,
            description="Validation error.",
        ),
        401: OpenApiResponse(
            response=ERROR_401_SCHEMA,
            description="Unauthorized.",
        ),
        403: OpenApiResponse(
            response=ERROR_403_SCHEMA,
            description="Forbidden.",
        ),
        404: OpenApiResponse(
            response=ERROR_404_SCHEMA,
            description="Not found.",
        ),
        429: OpenApiResponse(
            response=ERROR_429_SCHEMA,
            description="Too many requests.",
        ),
    },
    examples=[
        OpenApiExample(
            "Register request example",
            request_only=True,
            value={
                "email": "newuser@gmail.com",
                "password": "StrongPass123!",
                "first_name": "Boris",
                "last_name": "Dubovoy"
            },
        ),
        OpenApiExample(
            "Register success response example",
            response_only=True,
            status_codes=["201"],
            value={
                "id": 1,
                "email": "newuser@gmail.com",
                "first_name": "Boris",
                "last_name": "Dubovoy"
            },
        ),
    ],
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
    tags=["Auth"],
    summary="Get current user",
    description=(
        "Returns the currently authenticated user. "
        "Authentication is required."
    ),
    responses={
        200: OpenApiResponse(
            response=UserSerializer,
            description="Current user was returned successfully.",
        ),
        400: OpenApiResponse(
            response=ERROR_400_SCHEMA,
            description="Bad request.",
        ),
        401: OpenApiResponse(
            response=ERROR_401_SCHEMA,
            description="Unauthorized.",
        ),
        403: OpenApiResponse(
            response=ERROR_403_SCHEMA,
            description="Forbidden.",
        ),
        404: OpenApiResponse(
            response=ERROR_404_SCHEMA,
            description="Not found.",
        ),
        429: OpenApiResponse(
            response=ERROR_429_SCHEMA,
            description="Too many requests.",
        ),
    },
    examples=[
        OpenApiExample(
            "User me response example",
            response_only=True,
            status_codes=["200"],
            value={
                "id": 1,
                "email": "admin@gmail.com",
                "first_name": "Admin",
                "last_name": "User"
            },
        ),
    ],
)
class UserMeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(
    tags=["Auth"],
    summary="Change current user password",
    description=(
        "Changes the password for the currently authenticated user. "
        "Authentication is required. "
        "The request body must contain the old password and the new password."
    ),
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(
            response=ChangePasswordResponseSerializer,
            description="Password was changed successfully.",
        ),
        400: OpenApiResponse(
            response=ERROR_400_SCHEMA,
            description="Validation error or wrong old password.",
        ),
        401: OpenApiResponse(
            response=ERROR_401_SCHEMA,
            description="Unauthorized.",
        ),
        403: OpenApiResponse(
            response=ERROR_403_SCHEMA,
            description="Forbidden.",
        ),
        404: OpenApiResponse(
            response=ERROR_404_SCHEMA,
            description="Not found.",
        ),
        429: OpenApiResponse(
            response=ERROR_429_SCHEMA,
            description="Too many requests.",
        ),
    },
    examples=[
        OpenApiExample(
            "Change password request example",
            request_only=True,
            value={
                "old_password": "OldPass123!",
                "new_password": "NewStrongPass123!"
            },
        ),
        OpenApiExample(
            "Change password success response example",
            response_only=True,
            status_codes=["200"],
            value={
                "status": "password changed"
            },
        ),
        OpenApiExample(
            "Wrong old password response example",
            response_only=True,
            status_codes=["400"],
            value={
                "old_password": ["Wrong password."]
            },
        ),
    ],
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
    tags=["Auth"],
    summary="List users",
    description=(
        "Returns a list of users. Authentication is not required."
    ),
    responses={
        200: OpenApiResponse(
            response=ListUserSerializer(many=True),
            description="Users were returned successfully.",
        ),
        400: OpenApiResponse(
            response=ERROR_400_SCHEMA,
            description="Bad request.",
        ),
        401: OpenApiResponse(
            response=ERROR_401_SCHEMA,
            description="Unauthorized.",
        ),
        403: OpenApiResponse(
            response=ERROR_403_SCHEMA,
            description="Forbidden.",
        ),
        404: OpenApiResponse(
            response=ERROR_404_SCHEMA,
            description="Not found.",
        ),
        429: OpenApiResponse(
            response=ERROR_429_SCHEMA,
            description="Too many requests.",
        ),
    },
    examples=[
        OpenApiExample(
            "List users response example",
            response_only=True,
            status_codes=["200"],
            value=[
                {
                    "id": 1,
                    "email": "admin@gmail.com",
                    "first_name": "Admin",
                    "last_name": "User"
                },
                {
                    "id": 2,
                    "email": "user@gmail.com",
                    "first_name": "Test",
                    "last_name": "User"
                }
            ],
        ),
    ],
)
class ListUserView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=["Auth"],
    summary="Retrieve user by id",
    description=(
        "Returns a single user by id. Authentication is not required."
    ),
    responses={
        200: OpenApiResponse(
            response=RetrieveUserSerializer,
            description="User was returned successfully.",
        ),
        400: OpenApiResponse(
            response=ERROR_400_SCHEMA,
            description="Bad request.",
        ),
        401: OpenApiResponse(
            response=ERROR_401_SCHEMA,
            description="Unauthorized.",
        ),
        403: OpenApiResponse(
            response=ERROR_403_SCHEMA,
            description="Forbidden.",
        ),
        404: OpenApiResponse(
            response=ERROR_404_SCHEMA,
            description="User was not found.",
        ),
        429: OpenApiResponse(
            response=ERROR_429_SCHEMA,
            description="Too many requests.",
        ),
    },
    examples=[
        OpenApiExample(
            "Retrieve user response example",
            response_only=True,
            status_codes=["200"],
            value={
                "id": 1,
                "email": "admin@gmail.com",
                "first_name": "Admin",
                "last_name": "User"
            },
        ),
        OpenApiExample(
            "Retrieve user not found example",
            response_only=True,
            status_codes=["404"],
            value={
                "detail": "Not found."
            },
        ),
    ],
)
class RetrieveUserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = RetrieveUserSerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=["Auth"],
    summary="Login and get JWT tokens",
    description=(
        "Authenticates a user and returns JWT access and refresh tokens. "
        "Authentication is not required. "
        "The request body must contain the credentials required by the login serializer."
    ),
    request=LoginRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=TokenPairResponseSerializer,
            description="Tokens were returned successfully.",
        ),
        400: OpenApiResponse(
            response=ERROR_400_SCHEMA,
            description="Validation error or invalid credentials.",
        ),
        401: OpenApiResponse(
            response=ERROR_401_SCHEMA,
            description="Unauthorized.",
        ),
        403: OpenApiResponse(
            response=ERROR_403_SCHEMA,
            description="Forbidden.",
        ),
        404: OpenApiResponse(
            response=ERROR_404_SCHEMA,
            description="Not found.",
        ),
        429: OpenApiResponse(
            response=ERROR_429_SCHEMA,
            description="Too many requests.",
        ),
    },
    examples=[
        OpenApiExample(
            "Login request example",
            request_only=True,
            value={
                "email": "admin@gmail.com",
                "password": "admin"
            },
        ),
        OpenApiExample(
            "Login success response example",
            response_only=True,
            status_codes=["200"],
            value={
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh",
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access"
            },
        ),
    ],
)
class LoginView(TokenObtainPairView):
    pass


@extend_schema(
    tags=["Auth"],
    summary="Refresh access token",
    description=(
        "Returns a new access token using a valid refresh token. "
        "Authentication is not required. "
        "The request body must contain the refresh token."
    ),
    request=TokenRefreshRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=TokenRefreshResponseSerializer,
            description="Access token was refreshed successfully.",
        ),
        400: OpenApiResponse(
            response=ERROR_400_SCHEMA,
            description="Validation error or invalid refresh token.",
        ),
        401: OpenApiResponse(
            response=ERROR_401_SCHEMA,
            description="Unauthorized.",
        ),
        403: OpenApiResponse(
            response=ERROR_403_SCHEMA,
            description="Forbidden.",
        ),
        404: OpenApiResponse(
            response=ERROR_404_SCHEMA,
            description="Not found.",
        ),
        429: OpenApiResponse(
            response=ERROR_429_SCHEMA,
            description="Too many requests.",
        ),
    },
    examples=[
        OpenApiExample(
            "Refresh token request example",
            request_only=True,
            value={
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh"
            },
        ),
        OpenApiExample(
            "Refresh token success response example",
            response_only=True,
            status_codes=["200"],
            value={
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new_access"
            },
        ),
    ],
)
class RefreshTokenView(TokenRefreshView):
    pass