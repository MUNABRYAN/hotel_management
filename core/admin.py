from django.contrib import admin
from .models import UbicacionHabitacion, CaracteristicaHabitacion

@admin.register(UbicacionHabitacion)
class UbicacionHabitacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    search_fields = ['nombre']

@admin.register(CaracteristicaHabitacion)
class CaracteristicaHabitacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono', 'activo']
    search_fields = ['nombre']