from django.urls import path
from . import views

urlpatterns = [
    path('', views.default_route, name='default_route'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('register_raspberry/', views.register_raspberry, name='register_raspberry'),
    path('pid_register/<str:raspberry_id>/', views.pid_register, name='pid_register'),
    # path('start_subprocess/', views.start_subprocess, name='start_subprocess'),
    path('poll_data/', views.poll_data, name='poll_data'),
    path('sensors/', views.sensors, name='sensors'),
    path('start/', views.start, name='start'),
    path('end/', views.end, name='end')
]
