import os
from datetime import timedelta

try:
    from decouple import config as decouple_config
except ImportError:
    decouple_config = None


ENV_POSSIBLE_OPTIONS = (
    "local",
    "prod",
)


def _to_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def get_env(name, default=None, cast=str):
    if decouple_config is not None:
        return decouple_config(name, default=default, cast=cast)

    value = os.getenv(name, default)
    if value is None:
        return None
    if cast is bool:
        return _to_bool(value)
    return cast(value) if cast else value


ENV_ID = get_env("ULDAR_NET_ENV_ID", default="local")
SECRET_KEY = get_env("ULDAR_NET_SECRET_KEY", default="change-me-in-env")
DEBUG = get_env("ULDAR_NET_DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = [
    host.strip()
    for host in get_env("ULDAR_NET_ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=str).split(",")
    if host.strip()
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_ALL_ORIGINS = True