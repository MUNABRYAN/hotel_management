from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPersonalizado
from .models import Cargo, Turno, Empleado, TipoCliente
from .models import Cliente

@admin.register(UsuarioPersonalizado)
class UsuarioPersonalizadoAdmin(UserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'rol', 'is_active']
    list_filter = ['rol', 'is_active']
    
    # Campos adicionales en el formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información del Hotel', {
            'fields': ('rol', 'foto', 'telefono')
        }),
    )

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'hora_inicio', 'hora_fin', 'color']

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['cedula', 'nombre_completo', 'cargo', 'turno', 'celular', 'activo_en_hotel']
    search_fields = ['cedula', 'nombres', 'apellidos']
    list_filter = ['cargo', 'turno']

@admin.register(TipoCliente)
class TipoClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descuento', 'color', 'activo']



@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['rif', 'nombre', 'tipo', 'telefono']    