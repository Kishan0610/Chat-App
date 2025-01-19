from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/chat/<str:recipient>/', ChatConsumer.as_asgi()),  # Dynamic recipient in URL
]
