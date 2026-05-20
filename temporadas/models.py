"""
Modelos de Temporadas y Tarifas Dinámicas.
FASE 2: Una habitación tiene diferentes precios según la temporada.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import BaseModel
from hotel.models import TipoHabitacion


class TipoTemporada(BaseModel):
    """
    Categoría de temporada con color identificativo.
    Ejemplos: 'Temporada Alta' (rojo), 'Temporada Baja' (verde), 'Festivo' (dorado)
    
    El color se usa en el calendario visual.
    """
    nombre = models.CharField(max_length=100, unique=True)
    color = models.CharField(
        max_length=7,
        default='#007bff',
        help_text='Color en formato hexadecimal. Ej: #FF0000 para rojo'
    )
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Tipo de Temporada"
        verbose_name_plural = "Tipos de Temporada"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Temporada(BaseModel):
    """
    Rango de fechas que pertenece a un Tipo de Temporada.
    Ejemplo: 'Vacaciones de Verano' del 01-07-2026 al 31-08-2026 (Tipo: Alta)
    
    Una temporada puede tener múltiples rangos de fechas durante el año.
    """
    tipo = models.ForeignKey(
        TipoTemporada,
        on_delete=models.PROTECT,
        related_name='temporadas'
    )
    nombre = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    año = models.PositiveSmallIntegerField(
        help_text='Año al que pertenece esta temporada'
    )

    class Meta:
        verbose_name = "Temporada"
        verbose_name_plural = "Temporadas"
        ordering = ['año', 'fecha_inicio']

    def __str__(self):
        return f"{self.nombre} ({self.fecha_inicio:%d/%m} - {self.fecha_fin:%d/%m}/{self.año})"

    def clean(self):
        if self.fecha_inicio > self.fecha_fin:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin.')

    @classmethod
    def obtener_temporada_activa(cls, fecha=None):
        """
        Dada una fecha, devuelve la temporada activa.
        Si no hay temporada definida, devuelve None.
        """
        if fecha is None:
            fecha = timezone.now().date()
        return cls.objects.filter(
            fecha_inicio__lte=fecha,
            fecha_fin__gte=fecha,
            activo=True
        ).select_related('tipo').first()


class TarifaHabitacion(BaseModel):
    """
    Precio de un Tipo de Habitación para una temporada específica.
    
    EJEMPLO:
    Suite Junior + Temporada Alta = $250/noche
    Suite Junior + Temporada Baja = $150/noche
    Habitación Doble + Temporada Alta = $120/noche
    """
    tipo_habitacion = models.ForeignKey(
        TipoHabitacion,
        on_delete=models.CASCADE,
        related_name='tarifas'
    )
    tipo_temporada = models.ForeignKey(
        TipoTemporada,
        on_delete=models.CASCADE,
        related_name='tarifas'
    )
    precio_por_noche = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = "Tarifa de Habitación"
        verbose_name_plural = "Tarifas de Habitaciones"
        unique_together = ['tipo_habitacion', 'tipo_temporada']

    def __str__(self):
        return f"{self.tipo_habitacion} - {self.tipo_temporada}: ${self.precio_por_noche}"