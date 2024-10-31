from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter

from django.core.asgi import get_asgi_application
from django.urls import path, re_path


import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_security.settings')


from api.consumers.enter_exit import *
from api.consumers.closed_room import ClosedRoomConsumer
from api.consumers.room.room_camera import RoomCameraConsumer
from api.consumers.room.room_assistant import RoomAssistantConsumer

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('enter/<str:secret_key>', EnterConsumer.as_asgi()),
            path('exit/<str:secret_key>', ExitConsumer.as_asgi()),
            path('closed_room/<str:secret_key>', ClosedRoomConsumer.as_asgi()),

            path("room/camera/<str:secret_key>", RoomCameraConsumer.as_asgi()),
            path("room/assistant/<str:secret_key>", RoomAssistantConsumer.as_asgi())
        ])
    )
})