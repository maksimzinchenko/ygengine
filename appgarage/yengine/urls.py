from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('timenow', views.timenow, name='timenow'),
    path('infoblock/<str:infoblock_key>/', views.infoblock, name='infoblock'),
    path('audio/<str:stream_key>/', views.audio, name='audio'),
    path('stream/<str:stream_key>/', views.stream, name='stream'),
    path('sync/<str:stream_key>/', views.sync, name='sync'),
]