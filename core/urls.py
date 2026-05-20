from django.urls import path
from . import views, cruds

app_name = 'core'

def generar_crud(config, prefijo):
    prefijo = prefijo.rstrip('/')
    # Reemplazar guiones por guiones bajos en el nombre de URL
    url_name = prefijo.replace('-', '_')
    return [
        path(f'{prefijo}/', views.GenericListView.as_view(config=config), name=f'crud_{url_name}'),
        path(f'{prefijo}/nuevo/', views.GenericCreateView.as_view(config=config), name=f'crud_{url_name}_crear'),
        path(f'{prefijo}/<int:pk>/editar/', views.GenericUpdateView.as_view(config=config), name=f'crud_{url_name}_editar'),
        path(f'{prefijo}/<int:pk>/eliminar/', views.GenericDeleteView.as_view(config=config), name=f'crud_{url_name}_eliminar'),
    ]

urlpatterns = []
urlpatterns += generar_crud(cruds.UbicacionCrud, 'ubicaciones/')
urlpatterns += generar_crud(cruds.CaracteristicaCrud, 'caracteristicas/')
urlpatterns += generar_crud(cruds.TipoHabitacionCrud, 'tipos-habitacion/')
urlpatterns += generar_crud(cruds.HuespedCrud, 'huespedes/')
urlpatterns += generar_crud(cruds.TipoTemporadaCrud, 'tipos-temporada/')
urlpatterns += generar_crud(cruds.ProductoCrud, 'productos/')
urlpatterns += generar_crud(cruds.GrupoProductoCrud, 'grupos/')
urlpatterns += generar_crud(cruds.CargoCrud, 'cargos/')
urlpatterns += generar_crud(cruds.TurnoCrud, 'turnos/')
urlpatterns += generar_crud(cruds.EmpleadoCrud, 'empleados/')
urlpatterns += generar_crud(cruds.TipoClienteCrud, 'tipos-cliente/')
urlpatterns += generar_crud(cruds.HabitacionCrud, 'habitaciones/')
urlpatterns += generar_crud(cruds.TemporadaCrud, 'temporadas')
urlpatterns += generar_crud(cruds.TarifaCrud, 'tarifas')
urlpatterns += generar_crud(cruds.ClienteCrud, 'clientes/')




