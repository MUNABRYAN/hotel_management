"""
Modelos base para todo el proyecto.
Implementa el patrón SoftDelete y timestamps automáticos.
"""
from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """
    Manager personalizado que FILTRA POR DEFECTO los registros activos.
    Para acceder a TODOS los registros (incluyendo eliminados) usar:
    MiModelo.todos.all()
    """

    def get_queryset(self):
        # Por defecto, solo devolvemos registros NO eliminados
        return super().get_queryset().filter(activo=True)

    def incluir_eliminados(self):
        """Método auxiliar para obtener TODOS los registros sin filtrar."""
        return super().get_queryset()


class BaseModel(models.Model):
    """
    Modelo abstracto base para TODOS los modelos del sistema.
    Proporciona:
    - Timestamps automáticos (created_at, updated_at)
    - Soft Delete (activo = False en lugar de borrar)
    - Manager personalizado que oculta registros eliminados

    NO CREA TABLA EN LA BASE DE DATOS (es abstracto).
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
        help_text="Se establece automáticamente al crear el registro"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
        help_text="Se actualiza automáticamente en cada save()"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="False = eliminación lógica (soft delete)"
    )

    # Managers
    objects = SoftDeleteManager()  # Por defecto: solo activos
    todos = models.Manager()  # Manager sin filtrar (accede a eliminados también)

    def soft_delete(self):
        """
        Eliminación lógica: marca como inactivo en lugar de borrar de la BD.
        Ventaja: preservamos historial y relaciones.
        """
        self.activo = False
        self.save(update_fields=['activo', 'updated_at'])

    def restaurar(self):
        """Restaura un registro eliminado lógicamente."""
        self.activo = True
        self.save(update_fields=['activo', 'updated_at'])

    class Meta:
        abstract = True  # ESTO ES CLAVE: no crea tabla en BD
        ordering = ['-created_at']  # Por defecto, más recientes primero

    def __str__(self):
        # Método básico, cada modelo hijo lo sobrescribirá
        return f"{self.__class__.__name__} #{self.pk}"
    

# =============================================================================
# MODELOS DE SOPORTE PARA EL HOTEL
# Estos modelos son "catálogos" referenciados por Habitación
# =============================================================================

class UbicacionHabitacion(BaseModel):
    """
    Ubicación física de una habitación dentro del hotel.
    Ejemplos: 'Torre A - Piso 3', 'Ala Norte', 'Vista al mar', 'Vista al jardín'
    
    ¿Por qué es un modelo aparte y no un simple CharField?
    - Normalización: Si 50 habitaciones están en 'Torre A', guardas el texto UNA vez
    - Mantenibilidad: Cambiar 'Torre A' a 'Torre Principal' es UNA actualización
    - Reportes: Puedes filtrar fácilmente "todas las habitaciones con vista al mar"
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la ubicación"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Opcional: detalle adicional sobre esta ubicación"
    )

    class Meta:
        verbose_name = "Ubicación de habitación"
        verbose_name_plural = "Ubicaciones de habitaciones"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class CaracteristicaHabitacion(BaseModel):
    """
    Características o amenities de una habitación.
    Ejemplos: 'WiFi', 'TV Cable', 'Jacuzzi', 'Aire Acondicionado', 'Minibar'
    
    ¿Por qué ManyToMany y no campos booleanos?
    - Extensibilidad: Agregar nueva característica NO requiere migración de esquema
    - Búsqueda: "Quiero habitaciones con Jacuzzi Y WiFi" → simple filtro M2M
    - El gerente puede agregar características desde el admin sin tocar código
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Característica"
    )
    icono = models.CharField(
        max_length=50,
        blank=True,
        default='bi-check-circle',
        verbose_name="Icono Bootstrap",
        help_text="Clase de Bootstrap Icons. Ej: bi-wifi, bi-tv, bi-droplet"
    )

    class Meta:
        verbose_name = "Característica de habitación"
        verbose_name_plural = "Características de habitaciones"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
    


# =============================================================================
# MIXINS PARA VISTAS GENÉRICAS (Principio DRY)
# =============================================================================
from django.urls import reverse_lazy


class AdminMixin:
    """
    Mixin base para todas las vistas de administración.
    Agrega control de acceso y configuración común.
    """
    login_url = '/accounts/login/'
    # En producción, agregar: permission_required = 'usuarios.es_admin'


class CrudConfig:
    """
    Configuración base para CRUD genéricos.
    Cada entidad sobreescribe sus propios valores.
    """
    model = None
    fields = '__all__'
    list_display = ['id', 'nombre']
    search_fields = ['nombre']
    success_url = None
    template_list = 'core/generic_list.html'
    template_form = 'core/generic_form.html'
    template_confirm_delete = 'core/generic_confirm_delete.html'
    prefix_url = ''
    titulo_plural = 'Registros'
    titulo_singular = 'Registro'
    icono = 'bi-gear'    


class PisoSeccion(BaseModel):
    """
    Agrupación de habitaciones. Puede ser piso, chalet, bungalow, bloque, etc.
    """
    TIPO_CHOICES = [
        ('PISO', 'Piso'),
        ('CHALET', 'Chalet'),
        ('BUNGALOW', 'Bungalow'),
        ('BLOQUE', 'Bloque'),
        ('ALA', 'Ala'),
        ('CABAÑA', 'Cabaña'),
    ]
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='PISO')
    orden = models.PositiveSmallIntegerField(default=1)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Piso / Sección"
        verbose_name_plural = "Pisos / Secciones"
        ordering = ['orden', 'nombre']

    def __str__(self):
        return f"{self.nombre}"    