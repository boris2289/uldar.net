# Python modules
import os
# Django modules
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

# Project modules
from settings.conf import ENV_ID, ENV_POSSIBLE_OPTIONS
from apps.chat.routing import websocket_urlpatterns

assert ENV_ID in ENV_POSSIBLE_OPTIONS, f"Invalid env id. Possible options {ENV_POSSIBLE_OPTIONS}"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'settings.env.{ENV_ID}')

asgi = get_asgi_application()
application = ProtocolTypeRouter({
    "http": asgi,
    "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
                )
        )
}
)
