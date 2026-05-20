"""
URLs de autenticación y gestión de usuarios.
"""
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.LoginViewPersonalizado.as_view(), name='login'),
    path('logout/', views.LogoutViewPersonalizado.as_view(), name='logout'),
]