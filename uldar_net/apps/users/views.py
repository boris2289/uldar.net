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
from logging import getLogger


# Project imports 
from apps.users.models import CustomUser
from apps.users.serializers import (
    UserLoginSerializer,
    UserLoginFailSerializer,
    UserRegisterResponseSerializer,
    UserRegisterFailSerializer,
    UserRegisterSerializer
)
from apps.users.decorators import validate_serializer_data
from apps.common.responses import ERROR_401, ERROR_403, ERROR_404, ERROR_429, VALIDATION_400
from apps.tasks import send_confirmation_mail

logger = getLogger("django")

class CustomUserViewSet(ViewSet):
    """
    
    ViewSet for Custom User model

    """
    
    permission_classes = (IsAuthenticated,)

    def _get_log_context(self, request: DRFRequest) -> dict:
        """Helper to create consistent base logging context."""
        context = {
            "path": request.path,
            "method": request.method,
            "ip_address": request.META.get('REMOTE_ADDR'),
            "user_agent": request.META.get('HTTP_USER_AGENT'),
        }
        if request.user.is_authenticated:
            context["user_id"] = request.user.id
        return context

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
        log_extra = self._get_log_context(request)
        serializer: UserLoginSerializer = kwargs['serializer']
        try:
            user: CustomUser = serializer.validated_data.pop('user')
            refresh_token: RefreshToken = RefreshToken.for_user(user)
            
            log_extra["user_id"] = user.id
            log_extra["email"] = user.email
            
            logger.info(f"User login successful: {user.email}", extra=log_extra)
            
            return DRFResponse(
                data={
                    'id': user.id,
                    'email': user.email,
                    'access': str(refresh_token.access_token),
                    'refresh': str(refresh_token)
                },
                status=HTTP_200_OK
            )
        except Exception as e:
            log_extra["error"] = str(e)
            logger.error("Unexpected error during login process", extra=log_extra)
            return DRFResponse({"detail": "An internal error occurred"}, status=500)
        

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
        
        log_extra = self._get_log_context(request)
        serializer: UserRegisterSerializer = kwargs['serializer']
        data = serializer.validated_data

        try:
            user: CustomUser = CustomUser.objects.create_user(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                password=data['password'],
            )
            
            log_extra["user_id"] = user.id
            log_extra["email"] = user.email
            logger.info(f"New user registered: {user.email}", extra=log_extra)
            send_confirmation_mail.delay(user_email=user.email)
            return DRFResponse(
                data={
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                },
                status=HTTP_201_CREATED
            )
        except Exception as e:
            log_extra["error"] = str(e)
            log_extra["attempted_email"] = data.get('email')
            logger.warning("User registration failed", extra=log_extra)
            return DRFResponse({"detail": "Registration failed"}, status=HTTP_400_BAD_REQUEST) 
    
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
        """Return a new access token from a refresh token with improved logging."""
        refresh = request.data.get('refresh')
        
        # Use a dictionary for extra context if your logger supports it
        log_extra = {
            "path": request.path,
            "method": request.method,
            "user_agent": request.META.get('HTTP_USER_AGENT')
        }

        if not refresh:
            logger.warning("Token refresh failed: Missing refresh token", extra=log_extra)
            return DRFResponse({"detail": "Refresh token required"}, status=HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh)
            
            # Add user context once the token is decoded successfully
            log_extra["user_id"] = token.get("user_id")
            
            logger.info("Token refresh successful", extra=log_extra)
            return DRFResponse({"access": str(token.access_token)}, status=HTTP_200_OK)

        except Exception as e:
            # Log the actual exception type for easier debugging
            log_extra["error_detail"] = str(e)
            logger.warning("Token refresh failed: Invalid or expired token", extra=log_extra)
            return DRFResponse({"detail": "Invalid refresh token"}, status=HTTP_401_UNAUTHORIZED)

