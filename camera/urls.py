from django.urls import path
from . import stream_handler

urlpatterns = [
    path('live-feed/', stream_handler.live_feed_view, name='live_feed'),
]