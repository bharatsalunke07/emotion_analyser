from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('api/start/', views.start_detection, name='start_detection'),
    path('api/stop/', views.stop_detection, name='stop_detection'),
    path('api/status/', views.status, name='status'),
]
