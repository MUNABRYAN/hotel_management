from django.contrib import admin
from .models import TipoTemporada, Temporada, TarifaHabitacion


@admin.register(TipoTemporada)
class TipoTemporadaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'color', 'activo']
    search_fields = ['nombre']


@admin.register(Temporada)
class TemporadaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'año', 'fecha_inicio', 'fecha_fin', 'activo']
    list_filter = ['año', 'tipo']


@admin.register(TarifaHabitacion)
class TarifaHabitacionAdmin(admin.ModelAdmin):
    list_display = ['tipo_habitacion', 'tipo_temporada', 'precio_por_noche']
    list_filter = ['tipo_temporada']