from django.urls import path
from . import views

urlpatterns = [
    path('', views.default_route, name='default_route'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('register_raspberry/', views.register_raspberry, name='register_raspberry'),
    path('get_microservice_port/<str:raspberry_id>/', views.get_microservice_port, name='get_microservice_port'),
    path('start_subprocess/', views.start_subprocess, name='start_subprocess')
]
