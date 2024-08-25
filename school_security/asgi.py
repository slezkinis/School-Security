from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter

from django.core.asgi import get_asgi_application
from django.urls import path, re_path


import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_security.settings')


from api.consumers import *

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('enter/', EnterConsumer.as_asgi()),
            path('exit/', ExitConsumer.as_asgi()),
            # re_path(r"кщщь/(?P<room_name>\w+)/$",) для голосового помощника и камер в комнатах.
        ])
    )
})