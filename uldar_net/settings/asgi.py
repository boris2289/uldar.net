# Python modules
import os
# Django modules
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from django.urls import path

# Project modules
from settings.conf import ENV_ID, ENV_POSSIBLE_OPTIONS
from apps.consumers import AdminChatConsumer, PublicChatConsumer


assert ENV_ID in ENV_POSSIBLE_OPTIONS, f"Invalid env id. Possible options {ENV_POSSIBLE_OPTIONS}"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'settings.env.{ENV_ID}')

asgi = get_asgi_application()
application = ProtocolTypeRouter({
    "http": asgi,
    "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter([
                    path("chat/admin/", AdminChatConsumer.as_asgi()),
                    path("chat/", PublicChatConsumer.as_asgi())
                ])
                )
        )
}
)
