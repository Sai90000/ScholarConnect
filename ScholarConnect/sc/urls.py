from django.urls import path
from . import views

urlpatterns = [
    path('', views.initial, name='check'),
    path('get_api/', views.get_api, name='get_api')
]
