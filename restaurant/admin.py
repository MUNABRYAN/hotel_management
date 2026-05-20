from django.contrib import admin
from .models import GrupoProducto, Producto, ConsumoHabitacion
from .models import MenuDelDia, MenuItem, CierreCaja


@admin.register(GrupoProducto)
class GrupoProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'aplicacion', 'activo']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descripcion', 'grupo', 'precio_publico', 'precio_huesped', 'disponible']
    list_filter = ['grupo', 'aplicacion', 'disponible']
    search_fields = ['codigo', 'descripcion']

@admin.register(ConsumoHabitacion)
class ConsumoHabitacionAdmin(admin.ModelAdmin):
    list_display = ['registro_hospedaje', 'producto', 'cantidad', 'precio_unitario', 'subtotal', 'estado']
    list_filter = ['estado']


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1

@admin.register(MenuDelDia)
class MenuDelDiaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha', 'precio', 'disponible']
    inlines = [MenuItemInline]

@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'total_hospedajes', 'total_restaurant_habitaciones', 'total_general', 'cerrado_por']
    readonly_fields = ['total_hospedajes', 'total_restaurant_publico', 'total_restaurant_habitaciones', 'total_general']
    