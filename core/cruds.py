"""
Configuraciones de CRUD para cada entidad.
Principio DRY: Solo definimos la configuración, las vistas se generan automáticamente.
"""
from django.urls import reverse_lazy
from core.models import CrudConfig, UbicacionHabitacion, CaracteristicaHabitacion
from hotel.models import TipoHabitacion, Huesped
from temporadas.models import TipoTemporada, Temporada, TarifaHabitacion
from restaurant.models import GrupoProducto, Producto
from usuarios.models import Cargo, Turno, Empleado, TipoCliente
from hotel.models import Habitacion
from core.models import PisoSeccion

class UbicacionCrud(CrudConfig):
    model = UbicacionHabitacion
    list_display = ['nombre', 'descripcion', 'activo']
    search_fields = ['nombre']
    success_url = reverse_lazy('core:crud_ubicaciones')
    prefix_url = '/configuracion/ubicaciones/'
    titulo_plural = 'Ubicaciones'
    titulo_singular = 'Ubicación'
    icono = 'bi-geo-alt'


class CaracteristicaCrud(CrudConfig):
    model = CaracteristicaHabitacion
    list_display = ['nombre', 'icono', 'activo']
    success_url = reverse_lazy('core:crud_caracteristicas')
    prefix_url = '/configuracion/caracteristicas/'
    titulo_plural = 'Características'
    titulo_singular = 'Característica'
    icono = 'bi-check-circle'


class TipoHabitacionCrud(CrudConfig):
    model = TipoHabitacion
    list_display = ['nombre', 'capacidad_maxima', 'activo']
    fields = ['nombre', 'capacidad_maxima', 'descripcion', 'caracteristicas']
    success_url = reverse_lazy('core:crud_tipos_habitacion')
    prefix_url = '/configuracion/tipos-habitacion/'
    titulo_plural = 'Tipos de Habitación'
    titulo_singular = 'Tipo de Habitación'
    icono = 'bi-tag'


class HuespedCrud(CrudConfig):
    model = Huesped
    list_display = ['documento_identidad', 'nombres', 'apellidos', 'nacionalidad', 'telefono', 'activo']
    search_fields = ['nombres', 'apellidos', 'documento_identidad']
    fields = ['nombres', 'apellidos', 'documento_identidad', 'nacionalidad', 'email', 'telefono', 'telefono_alternativo', 'fecha_nacimiento']
    success_url = reverse_lazy('core:crud_huespedes')
    prefix_url = '/configuracion/huespedes/'
    titulo_plural = 'Huéspedes'
    titulo_singular = 'Huésped'
    icono = 'bi-people'


class TipoTemporadaCrud(CrudConfig):
    model = TipoTemporada
    list_display = ['nombre', 'color', 'activo']
    success_url = reverse_lazy('core:crud_tipos_temporada')
    prefix_url = '/configuracion/tipos-temporada/'
    titulo_plural = 'Tipos de Temporada'
    titulo_singular = 'Tipo de Temporada'
    icono = 'bi-palette'


class ProductoCrud(CrudConfig):
    model = Producto
    list_display = ['codigo', 'descripcion', 'grupo', 'precio_publico', 'disponible']
    search_fields = ['codigo', 'descripcion']
    fields = ['codigo', 'descripcion', 'grupo', 'aplicacion', 'precio_publico', 'precio_huesped', 'precio_personal', 'disponible']
    success_url = reverse_lazy('core:crud_productos')
    prefix_url = '/configuracion/productos/'
    titulo_plural = 'Productos'
    titulo_singular = 'Producto'
    icono = 'bi-cup'


class GrupoProductoCrud(CrudConfig):
    model = GrupoProducto
    list_display = ['nombre', 'aplicacion', 'activo']
    success_url = reverse_lazy('core:crud_grupos')
    prefix_url = '/configuracion/grupos/'
    titulo_plural = 'Grupos de Productos'
    titulo_singular = 'Grupo'
    icono = 'bi-folder'

class CargoCrud(CrudConfig):
    model = Cargo
    list_display = ['nombre', 'descripcion', 'activo']
    fields = ['nombre', 'descripcion']
    success_url = reverse_lazy('core:crud_cargos')
    prefix_url = '/configuracion/cargos/'
    titulo_plural = 'Cargos'
    titulo_singular = 'Cargo'
    icono = 'bi-briefcase'


class TurnoCrud(CrudConfig):
    model = Turno
    list_display = ['nombre', 'hora_inicio', 'hora_fin', 'color', 'activo']
    fields = ['nombre', 'hora_inicio', 'hora_fin', 'color']
    success_url = reverse_lazy('core:crud_turnos')
    prefix_url = '/configuracion/turnos/'
    titulo_plural = 'Turnos'
    titulo_singular = 'Turno'
    icono = 'bi-clock'


class EmpleadoCrud(CrudConfig):
    model = Empleado
    list_display = ['cedula', 'nombres', 'apellidos', 'cargo', 'celular', 'activo']
    fields = ['cedula', 'nombres', 'apellidos', 'cargo', 'turno', 'direccion',
              'telefono_local', 'celular', 'email', 'fecha_nacimiento',
              'fecha_ingreso', 'fecha_egreso', 'motivo_egreso', 'foto']
    success_url = reverse_lazy('core:crud_empleados')
    prefix_url = '/configuracion/empleados/'
    titulo_plural = 'Empleados'
    titulo_singular = 'Empleado'
    icono = 'bi-person-badge'


class TipoClienteCrud(CrudConfig):
    model = TipoCliente
    list_display = ['nombre', 'descuento', 'color', 'activo']
    fields = ['nombre', 'descripcion', 'descuento', 'color']
    success_url = reverse_lazy('core:crud_tipos_cliente')
    prefix_url = '/configuracion/tipos-cliente/'
    titulo_plural = 'Tipos de Clientes'
    titulo_singular = 'Tipo de Cliente'
    icono = 'bi-person-check'    

class HabitacionCrud(CrudConfig):
    model = Habitacion
    list_display = ['codigo', 'nombre', 'tipo', 'ubicacion', 'piso', 'activo']
    fields = ['codigo', 'nombre', 'tipo', 'ubicacion', 'piso', 'extension_telefono', 'notas_internas']
    success_url = reverse_lazy('core:crud_habitaciones')
    prefix_url = '/configuracion/habitaciones/'
    titulo_plural = 'Habitaciones'
    titulo_singular = 'Habitación'
    icono = 'bi-door-open'    



class TemporadaCrud(CrudConfig):
    model = Temporada
    list_display = ['nombre', 'tipo', 'año', 'fecha_inicio', 'fecha_fin', 'activo']
    fields = ['tipo', 'nombre', 'año', 'fecha_inicio', 'fecha_fin']
    success_url = reverse_lazy('core:crud_temporadas')
    prefix_url = '/configuracion/temporadas/'
    titulo_plural = 'Temporadas'
    titulo_singular = 'Temporada'
    icono = 'bi-calendar-range'


class TarifaCrud(CrudConfig):
    model = TarifaHabitacion
    list_display = ['tipo_habitacion', 'tipo_temporada', 'precio_por_noche', 'activo']
    fields = ['tipo_habitacion', 'tipo_temporada', 'precio_por_noche']
    success_url = reverse_lazy('core:crud_tarifas')
    prefix_url = '/configuracion/tarifas/'
    titulo_plural = 'Tarifas'
    titulo_singular = 'Tarifa'
    icono = 'bi-cash'

from usuarios.models import Cliente

class ClienteCrud(CrudConfig):
    model = Cliente
    list_display = ['rif', 'nombre', 'tipo', 'telefono', 'email', 'activo']
    fields = ['tipo', 'rif', 'nombre', 'direccion_fiscal', 'telefono', 'email', 'tipo_cliente']
    success_url = reverse_lazy('core:crud_clientes')
    prefix_url = '/configuracion/clientes/'
    titulo_plural = 'Clientes'
    titulo_singular = 'Cliente'
    icono = 'bi-building'    

class PisoSeccionCrud(CrudConfig):
    model = PisoSeccion
    list_display = ['nombre', 'tipo', 'orden', 'activo']
    fields = ['nombre', 'tipo', 'orden', 'descripcion']
    success_url = reverse_lazy('core:crud_pisos_secciones')
    prefix_url = '/configuracion/pisos-secciones/'
    titulo_plural = 'Pisos / Secciones'
    titulo_singular = 'Piso / Sección'
    icono = 'bi-layers'