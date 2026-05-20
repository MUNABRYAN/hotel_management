"""
Configuración del admin de Django para modelos del hotel.
Esto nos permite probar los modelos rápidamente sin crear vistas aún.
"""
from django.contrib import admin
from .models import (
    TipoHabitacion, Habitacion, HabitacionFoto,
    EstadoHabitacion, Huesped, RegistroHospedaje
)
from .models import Reserva


class HabitacionFotoInline(admin.TabularInline):
    """Permite agregar/editar fotos DENTRO del formulario de Habitación."""
    model = HabitacionFoto
    extra = 1  # Muestra 1 fila vacía para nueva foto
    fields = ['imagen', 'es_principal', 'orden']


class EstadoHabitacionInline(admin.TabularInline):
    """Muestra el historial de estados DENTRO de Habitación."""
    model = EstadoHabitacion
    extra = 0  # Solo lectura, no agregar desde aquí
    fields = ['estado', 'fecha_inicio', 'fecha_fin', 'notas']
    readonly_fields = ['fecha_inicio', 'fecha_fin']
    can_delete = False


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo', 'ubicacion', 'estado_str', 'piso_seccion', 'activo']
    list_filter = ['tipo', 'ubicacion', 'piso_seccion', 'activo']
    search_fields = ['codigo', 'nombre']
    inlines = [HabitacionFotoInline, EstadoHabitacionInline]
    
    def estado_str(self, obj):
        """Muestra el estado actual con un ícono de color."""
        estado = obj.estado_actual
        if not estado:
            return "⚠️ Sin registro"
        iconos = {
            'DISPONIBLE': '🟢',
            'OCUPADA': '🔴',
            'SUCIA': '🟡',
            'MANTENIMIENTO': '⚫',
            'RESERVADA': '🔵',
        }
        return f"{iconos.get(estado.estado, '❓')} {estado.get_estado_display()}"
    estado_str.short_description = "Estado Actual"


@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad_maxima', 'activo']
    filter_horizontal = ['caracteristicas']


@admin.register(Huesped)
class HuespedAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'documento_identidad', 'nacionalidad', 'telefono']
    search_fields = ['nombres', 'apellidos', 'documento_identidad']


@admin.register(RegistroHospedaje)
class RegistroHospedajeAdmin(admin.ModelAdmin):
    list_display = ['huesped', 'habitacion', 'fecha_checkin', 'fecha_checkout', 'esta_activo', 'total_estadia']
    list_filter = ['fecha_checkin', 'fecha_checkout']
    readonly_fields = ['total_estadia']

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['huesped', 'habitacion', 'fecha_entrada', 'fecha_salida', 'estado', 'noches', 'total']
    list_filter = ['estado', 'fecha_entrada']
    search_fields = ['huesped__nombres', 'huesped__apellidos', 'habitacion__codigo']
    
        