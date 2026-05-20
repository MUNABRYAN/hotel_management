from django.urls import path
from . import views

app_name = 'hotel'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('habitaciones/', views.PanelHabitacionesView.as_view(), name='panel_habitaciones'),
    path('habitaciones/<int:pk>/', views.DetalleHabitacionView.as_view(), name='detalle_habitacion'),
    path('habitaciones/<int:pk>/cambiar-estado/', views.CambiarEstadoHabitacionView.as_view(), name='cambiar_estado_habitacion'),
    path('api/huespedes/', views.ListaHuespedesAPI.as_view(), name='api_huespedes'),
    path('api/huespedes/crear/', views.CrearHuespedAPI.as_view(), name='api_crear_huesped'),
    path('api/disponibilidad/', views.DisponibilidadAPI.as_view(), name='api_disponibilidad'),
    path('api/reservas/crear/', views.CrearReservaAPI.as_view(), name='api_crear_reserva'),
    path('reservas/nueva/', views.BuscarDisponibilidadView.as_view(), name='nueva_reserva'),

    path('cargos/', views.CargosHabitacionView.as_view(), name='cargos_habitacion'),
    path('api/habitaciones-ocupadas/', views.HabitacionesOcupadasAPI.as_view(), name='api_habitaciones_ocupadas'),
    path('api/productos/', views.ProductosAPI.as_view(), name='api_productos'),
    path('api/cargar-consumo/', views.CargarConsumoAPI.as_view(), name='api_cargar_consumo'),    
    path('api/calendario-eventos/', views.CalendarioEventosAPI.as_view(), name='api_calendario_eventos'),
    path('calendario/', views.CalendarioView.as_view(), name='calendario'),

    path('configuracion/habitaciones/', views.HabitacionListView.as_view(), name='crud_habitacion_lista'),
    path('configuracion/habitaciones/nueva/', views.HabitacionCreateView.as_view(), name='crud_habitacion_crear'),
    path('configuracion/habitaciones/<int:pk>/editar/', views.HabitacionUpdateView.as_view(), name='crud_habitacion_editar'),
    path('configuracion/habitaciones/<int:pk>/eliminar/', views.HabitacionDeleteView.as_view(), name='crud_habitacion_eliminar'),
    path('api/clientes/', views.ClientesAPI.as_view(), name='api_clientes'),
]


