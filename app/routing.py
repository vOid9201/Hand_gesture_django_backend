from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/video/', consumers.VideoConsumer.as_asgi()),
]