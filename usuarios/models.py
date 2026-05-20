"""
Modelo de usuario personalizado con roles para el sistema hotelero.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel


class UsuarioPersonalizado(AbstractUser):
    """
    Usuario personalizado que extiende el modelo User de Django.
    Añade:
    - Rol para control de permisos
    - Foto de perfil
    - Teléfono de contacto
    """

    class Rol(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        RECEPCION = 'RECEPCION', 'Recepción'
        GERENTE = 'GERENTE', 'Gerente'

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.RECEPCION,
        verbose_name="Rol del usuario",
        help_text="Determina los permisos y acceso al sistema"
    )
    foto = models.ImageField(
        upload_to='usuarios/fotos/',
        null=True,
        blank=True,
        verbose_name="Foto de perfil"
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono de contacto"
    )

    class Meta:
        verbose_name = "Usuario del sistema"
        verbose_name_plural = "Usuarios del sistema"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.rol})"

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN

    @property
    def es_recepcionista(self):
        return self.rol == self.Rol.RECEPCION

    @property
    def es_gerente(self):
        return self.rol == self.Rol.GERENTE
    


# =============================================================================
# MODELOS DE EMPLEADOS (FASE 5)
# =============================================================================

class Cargo(BaseModel):
    """
    Cargo laboral en el hotel.
    Ej: Recepcionista, Camarero, Chef, Gerente, Botones
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Turno(BaseModel):
    """
    Turno de trabajo.
    Ej: Mañana (7am-3pm), Tarde (3pm-11pm), Noche (11pm-7am)
    """
    nombre = models.CharField(max_length=100, unique=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    color = models.CharField(max_length=7, default='#6c757d')

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ['hora_inicio']

    def __str__(self):
        return f"{self.nombre} ({self.hora_inicio:%H:%M} - {self.hora_fin:%H:%M})"


class Empleado(BaseModel):
    """
    Empleado del hotel. Extiende al usuario del sistema o es independiente.
    """
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula")
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='empleados/fotos/', blank=True, null=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, related_name='empleados')
    turno = models.ForeignKey(Turno, on_delete=models.SET_NULL, null=True, blank=True, related_name='empleados')
    direccion = models.TextField(blank=True)
    telefono_local = models.CharField(max_length=20, blank=True, verbose_name="Teléfono Local")
    celular = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    fecha_egreso = models.DateField(null=True, blank=True)
    motivo_egreso = models.TextField(blank=True)
    usuario = models.OneToOneField(
        UsuarioPersonalizado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='empleado'
    )

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def activo_en_hotel(self):
        return self.fecha_egreso is None


class TipoCliente(BaseModel):
    """
    Categoría de cliente para asignar a huéspedes.
    Ej: Habitual, Turista, Viajero, VIP, Corporativo
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                     help_text="Porcentaje de descuento (0-100)")
    color = models.CharField(max_length=7, default='#007bff',
                              help_text="Color identificativo")

    class Meta:
        verbose_name = "Tipo de Cliente"
        verbose_name_plural = "Tipos de Clientes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
    

class Cliente(BaseModel):
    """
    Cliente facturable. Puede ser Natural (persona) o Jurídico (empresa).
    """
    TIPO_CHOICES = [
        ('NATURAL', 'Natural'),
        ('JURIDICO', 'Jurídico'),
    ]
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='NATURAL')
    rif = models.CharField(max_length=20, unique=True, verbose_name="RIF/Cédula")
    nombre = models.CharField(max_length=200, verbose_name="Nombre o Razón Social")
    direccion_fiscal = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    tipo_cliente = models.ForeignKey(TipoCliente, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    