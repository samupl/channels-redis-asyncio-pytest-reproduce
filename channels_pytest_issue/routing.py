from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from example_app.consumers import ExampleConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
            path('test/', ExampleConsumer.as_asgi()),
        ]),
})
