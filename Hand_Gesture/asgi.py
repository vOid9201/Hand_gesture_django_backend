import os
from django.urls import path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import app.routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hand_Gesture.settings')

application = ProtocolTypeRouter({
    'http' : get_asgi_application(),
    'websocket' : URLRouter(
        app.routing.websocket_urlpatterns 
    )
})
