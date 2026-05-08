# Python imports 
from typing import Any, Optional


# Django imports 
from django.core.exceptions import ValidationError

# Rest-Framework imports 
from rest_framework.viewsets import ViewSet
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
    ) 
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
) 


# Project imports 
from apps.users.models import CustomUser
from apps.users.serializers import *
from apps.users.decorators import validate_serializer_data
from apps.common.responses import ERROR_401, ERROR_403, ERROR_404, ERROR_429, VALIDATION_400


class CustomUserViewSet(ViewSet):
    """
    
    ViewSet for Custom User model

    """
    
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Users"],
        summary="Login",
        description="Used for authorization",
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(response=UserLoginSerializer(), description="Successful Login"),
            400: VALIDATION_400,
            401: ERROR_401,
            403: ERROR_403,
            404: ERROR_404,
            429: ERROR_429,
        },
        examples=[
            OpenApiExample(
                "Login response example",
                request_only=True,
                value={ 
                    'id' : 3,
                    'email' : "example@mail.com",
                    'access' : "skdjflksjdf",
                    'refresh' : "sdjflksdjfl"
                },
                status_codes=["200"],
                
            )
        ]
    )
    @action(
        methods=('POST',),
        detail=False,
        url_path='login',
        permission_classes = [AllowAny,]
    )
    @validate_serializer_data(serializer_class=UserLoginSerializer)
    def login(
        self,
        request : DRFRequest,
        *args : tuple[Any, ...],
        **kwargs : dict[str, Any]
    ) -> DRFResponse:
        """
        Handle Custom User login
        
        """

        serializer : UserLoginSerializer = kwargs['serializer']
        user : CustomUser = serializer.validated_data.pop('user')

        refresh_token : RefreshToken = RefreshToken.for_user(user)
        access_token : str = str(refresh_token.access_token)

        return DRFResponse(
            data={
                'id' : user.id,
                'email' : user.email,
                'access' : access_token,
                'refresh' : str(refresh_token)
            },
            status=HTTP_200_OK
        )

    @extend_schema(
        tags=["Users"],
        summary="Register",
        description="Register a new user. Sign up",
        request=UserRegisterSerializer,
        responses={
            201: OpenApiResponse(response=UserRegisterSerializer(), description="Successful Registration"),
            400: VALIDATION_400,
            401: ERROR_401,
            403: ERROR_403,
            404: ERROR_404,
            429: ERROR_429,
        },
        examples=[
            OpenApiExample(
                "Login response example",
                request_only=True,
                value={ 
                    'id': 3,
                    'first_name': "Sardelka",
                    'last_name': "Zefirov",
                    'email': "example@mail.ru",
                },
                status_codes=["201"],
                
            )
        ]
    )
    @action(
        methods=('POST',),
        url_path='register',
        detail=False,
        permission_classes = [AllowAny]
    )
    @validate_serializer_data(serializer_class=UserRegisterSerializer)
    def register(
        self,
        request : DRFRequest,
        *args : tuple[Any, ...],
        **kwargs : dict[str, Any]
    ) -> DRFResponse:
        
        serializer : UserRegisterSerializer = kwargs['serializer']
        data = serializer.validated_data

        user : CustomUser = CustomUser.objects.create_user(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
        )

        return DRFResponse(
            data={
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            },
            status=HTTP_201_CREATED
        )        
    
    @extend_schema(
        tags=["Users"],
        summary="Refresh Token",
        description="To remain logged in",
        responses={
            200: OpenApiResponse(response=inline_serializer(name="RefreshTokenSerializer", fields={"access": "asdhjkashdk"}), description="Token Refreshed"),
            400: VALIDATION_400,
            401: ERROR_401,
            403: ERROR_403,
            404: ERROR_404,
            429: ERROR_429,
        },
        examples=[
            OpenApiExample(
                "Login response example",
                request_only=True,
                value={ 
                    "access": "asdjklasjdlka"
                },
                status_codes=["200"],
                
            )
        ]
    )
    @action(
        methods=('POST',),
        detail=False,
        url_path='token/refresh',
        permission_classes=[AllowAny]
        )
    
    def refresh_token(self, request: DRFRequest) -> DRFResponse:
        """Return a new access token from a refresh token."""
        refresh = request.data.get('refresh')
        if not refresh:
            return DRFResponse({"detail": ("Refresh token required")}, status=HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh)
            return DRFResponse({"access": str(token.access_token)}, status=HTTP_200_OK)
        except Exception:
            return DRFResponse({"detail": ("Invalid refresh token")}, status=HTTP_401_UNAUTHORIZED)

