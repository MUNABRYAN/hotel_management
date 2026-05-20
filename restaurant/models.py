"""
Modelos del módulo Restaurant.
FASE 3: Productos, Menús y Cargos a habitación.
"""
from django.db import models
from django.core.exceptions import ValidationError
from core.models import BaseModel


class GrupoProducto(BaseModel):
    """
    Categoría de productos.
    Ej: Bebidas, Entradas, Platos Fuertes, Postres, Licores
    """
    APLICACION_CHOICES = [
        ('HOTEL', 'Hotel'),
        ('RESTAURANT', 'Restaurant'),
        ('AMBOS', 'Ambos'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True)
    aplicacion = models.CharField(max_length=15, choices=APLICACION_CHOICES, default='AMBOS')
    foto = models.ImageField(upload_to='grupos/', blank=True, null=True)

    class Meta:
        verbose_name = "Grupo de Producto"
        verbose_name_plural = "Grupos de Productos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_aplicacion_display()})"


class Producto(BaseModel):
    """
    Producto del restaurant o servicio del hotel.
    Tiene hasta 3 niveles de precio para diferentes contextos.
    """
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=200)
    grupo = models.ForeignKey(GrupoProducto, on_delete=models.PROTECT, related_name='productos')
    aplicacion = models.CharField(
        max_length=15,
        choices=GrupoProducto.APLICACION_CHOICES,
        default='AMBOS'
    )
    foto = models.ImageField(upload_to='productos/', blank=True, null=True)
    precio_publico = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Público General")
    precio_huesped = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Huésped", help_text="Precio especial para huéspedes del hotel")
    precio_personal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Personal", help_text="Precio para empleados")
    disponible = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['grupo', 'descripcion']

    def __str__(self):
        return f"[{self.codigo}] {self.descripcion}"

    def get_precio(self, tipo_cliente='PUBLICO'):
        """Retorna el precio según el tipo de cliente."""
        precios = {
            'PUBLICO': self.precio_publico,
            'HUESPED': self.precio_huesped,
            'PERSONAL': self.precio_personal,
        }
        return precios.get(tipo_cliente, self.precio_publico)


class ConsumoHabitacion(BaseModel):
    """
    Cargo a la habitación de un huésped.
    Un huésped pide algo en el restaurant y se carga a su cuenta.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('FACTURADO', 'Facturado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    registro_hospedaje = models.ForeignKey(
        'hotel.RegistroHospedaje',
        on_delete=models.PROTECT,
        related_name='consumos'
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveSmallIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PENDIENTE')
    notas = models.TextField(blank=True)
    fecha_consumo = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Consumo a Habitación"
        verbose_name_plural = "Consumos a Habitaciones"
        ordering = ['-fecha_consumo']

    def __str__(self):
        return f"{self.producto.descripcion} x{self.cantidad} → Hab. {self.registro_hospedaje.habitacion.codigo}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
    

class MenuDelDia(BaseModel):
    """
    Menú del día. Agrupa productos disponibles en una fecha específica.
    Ej: "Menú Ejecutivo 22-mayo" con entrada + plato + postre + bebida.
    """
    nombre = models.CharField(max_length=200)
    fecha = models.DateField()
    productos = models.ManyToManyField(Producto, through='MenuItem')
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio del menú completo")
    disponible = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Menú del Día"
        verbose_name_plural = "Menús del Día"
        ordering = ['-fecha']
        unique_together = ['nombre', 'fecha']

    def __str__(self):
        return f"Menú {self.fecha:%d/%m/%Y} - {self.nombre}"


class MenuItem(models.Model):
    """Relación entre Menú y Producto con categoría (entrada, plato, etc)."""
    CATEGORIA_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SOPA', 'Sopa'),
        ('PLATO', 'Plato Fuerte'),
        ('POSTRE', 'Postre'),
        ('BEBIDA', 'Bebida'),
    ]
    
    menu = models.ForeignKey(MenuDelDia, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=10, choices=CATEGORIA_CHOICES)

    class Meta:
        unique_together = ['menu', 'categoria']
        verbose_name = "Ítem del Menú"
        verbose_name_plural = "Ítems del Menú"

    def __str__(self):
        return f"{self.get_categoria_display()}: {self.producto.descripcion}"


from django.utils import timezone

class CierreCaja(BaseModel):
    """
    Cierre de caja diario.
    Registra total de ingresos por hospedaje y restaurant.
    """
    fecha = models.DateField(unique=True, default=timezone.now)
    total_hospedajes = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_restaurant_publico = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_restaurant_habitaciones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_general = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    cerrado_por = models.ForeignKey('usuarios.UsuarioPersonalizado', on_delete=models.PROTECT, null=True)

    class Meta:
        verbose_name = "Cierre de Caja"
        verbose_name_plural = "Cierres de Caja"
        ordering = ['-fecha']

    def __str__(self):
        return f"Cierre {self.fecha:%d/%m/%Y} - Total: ${self.total_general}"

    def calcular_totales(self):
        """Calcula los totales automáticamente."""
        from hotel.models import RegistroHospedaje
        from django.db.models import Sum

        # Check-outs del día
        hospedajes = RegistroHospedaje.objects.filter(
            fecha_checkout__date=self.fecha
        )
        self.total_hospedajes = sum(h.total_estadia for h in hospedajes) or 0

        # Consumos de restaurant cargados a habitación (facturados)
        consumos = ConsumoHabitacion.objects.filter(
            fecha_consumo__date=self.fecha,
            estado='FACTURADO'
        ).aggregate(total=Sum('precio_unitario'))['total'] or 0
        self.total_restaurant_habitaciones = consumos

        self.total_general = self.total_hospedajes + self.total_restaurant_publico + self.total_restaurant_habitaciones
        self.save()

        