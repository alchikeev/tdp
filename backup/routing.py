from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/restore/(?P<task_id>[0-9a-f-]+)/$', consumers.RestoreProgressConsumer.as_asgi()),
]
