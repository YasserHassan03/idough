from django.urls import path
from . import views

urlpatterns = [
    path('', views.default_route, name='default_route'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
]

