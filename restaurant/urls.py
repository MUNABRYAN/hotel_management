from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('menu/', views.MenuDiaListView.as_view(), name='menu_dia'),
    path('menu/nuevo/', views.CrearMenuView.as_view(), name='crear_menu'),
]


