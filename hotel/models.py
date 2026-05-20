"""
Modelos principales de gestión hotelera.
Contiene: TipoHabitacion, Habitacion, HabitacionFoto, EstadoHabitacion,
Huesped, RegistroHospedaje.

PRINCIPIO DE DISEÑO: Lógica de negocio EN EL MODELO, no en las vistas.
"""
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit

from core.models import BaseModel, UbicacionHabitacion, CaracteristicaHabitacion



# =============================================================================
# TIPO DE HABITACIÓN
# =============================================================================

class TipoHabitacion(BaseModel):
    """
    Categoría de habitación (Simple, Doble, Suite, Suite Presidencial).
    Define capacidad y características comunes a todas las habitaciones de este tipo.
    
    La tarifa NO está aquí porque varía por temporada (FASE 2).
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Tipo de habitación"
    )
    capacidad_maxima = models.PositiveSmallIntegerField(
        verbose_name="Capacidad máxima de personas",
        help_text="Número máximo de huéspedes permitidos"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción del tipo"
    )
    caracteristicas = models.ManyToManyField(
        CaracteristicaHabitacion,
        blank=True,
        verbose_name="Características incluidas",
        help_text="Amenities que incluye este tipo de habitación"
    )

    class Meta:
        verbose_name = "Tipo de habitación"
        verbose_name_plural = "Tipos de habitaciones"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (máx {self.capacidad_maxima} pers.)"


# =============================================================================
# HABITACIÓN
# =============================================================================

class Habitacion(BaseModel):
    """
    Habitación FÍSICA del hotel.
    Cada habitación tiene un código único, pertenece a un tipo y una ubicación.
    
    El ESTADO ACTUAL se obtiene del último registro en EstadoHabitacion,
    NO se almacena aquí (patrón Event Sourcing simplificado).
    """
    codigo = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Código",
        help_text="Ej: 101, 202A, PH-01"
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre descriptivo",
        help_text="Ej: 'Suite Imperial', 'Doble 101'"
    )
    tipo = models.ForeignKey(
        TipoHabitacion,
        on_delete=models.PROTECT,  # No permitir borrar tipo si hay habitaciones
        related_name='habitaciones',
        verbose_name="Tipo de habitación"
    )
    ubicacion = models.ForeignKey(
        UbicacionHabitacion,
        on_delete=models.PROTECT,
        related_name='habitaciones',
        verbose_name="Ubicación"
    )
    extension_telefono = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Extensión telefónica"
    )
    piso_seccion = models.ForeignKey(
        'core.PisoSeccion',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='habitaciones',
        verbose_name="Piso / Sección"
    )
    notas_internas = models.TextField(
        blank=True,
        verbose_name="Notas internas",
        help_text="Visible solo para empleados. Ej: 'Aire acondicionado ruidoso'"
    )

    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"
        ordering = ['piso_seccion__orden', 'codigo']

    def __str__(self):
        return f"Habitación {self.codigo} - {self.tipo.nombre}"

    # --- LÓGICA DE NEGOCIO (Aquí vive la inteligencia, NO en las vistas) ---

    @property
    def estado_actual(self):
        """
        Devuelve el ÚLTIMO registro de estado (el que está vigente).
        Retorna None si la habitación no tiene estados registrados.
        """
        try:
            return self.estados.filter(fecha_fin__isnull=True).latest('fecha_inicio')
        except EstadoHabitacion.DoesNotExist:
            return None

    @property
    def estado_str(self):
        """Representación en texto del estado actual."""
        estado = self.estado_actual
        return estado.estado if estado else 'SIN_REGISTRO'

    @property
    def esta_disponible(self):
        """¿La habitación se puede asignar a un huésped?"""
        estado = self.estado_actual
        return estado is not None and estado.estado == 'DISPONIBLE'

    @property
    def esta_ocupada(self):
        """¿Hay un huésped actualmente?"""
        estado = self.estado_actual
        return estado is not None and estado.estado == 'OCUPADA'

    @property
    def foto_principal(self):
        """Devuelve la primera foto marcada como principal, o la primera en orden."""
        foto = self.fotos.filter(es_principal=True).first()
        if not foto:
            foto = self.fotos.order_by('orden').first()
        return foto

    def cambiar_estado(self, nuevo_estado, notas=''):
        """
        Método ATÓMICO para cambiar el estado de la habitación.
        Cierra el estado anterior y crea uno nuevo.
        """
        with transaction.atomic():
            # 1. Cerrar estado actual (si existe)
            estado_anterior = self.estado_actual
            if estado_anterior:
                # Verificar que el estado anterior tiene fecha_fin antes de guardar
                estado_anterior.fecha_fin = timezone.now()
                # Solo actualizar fecha_fin, no updated_at (que no existe en algunos casos)
                estado_anterior.save(update_fields=['fecha_fin'])

            # 2. Crear nuevo estado
            nuevo = EstadoHabitacion.objects.create(
                habitacion=self,
                estado=nuevo_estado,
                fecha_inicio=timezone.now(),
                notas=notas
            )
            return nuevo
        

    def disponible_en_fechas(self, fecha_entrada, fecha_salida):
        """
        Verifica si la habitación está disponible en un rango de fechas.
        Comprueba:
        - Reservas confirmadas/pendientes que se solapen
        - Registros de hospedaje activos que se solapen
        """
        from datetime import date
        
        # Verificar reservas solapadas
        reservas_solapadas = Reserva.objects.filter(
            habitacion=self,
            estado__in=['CONFIRMADA', 'PENDIENTE'],
            fecha_entrada__lt=fecha_salida,
            fecha_salida__gt=fecha_entrada,
        ).exists()
        
        if reservas_solapadas:
            return False
        
        # Verificar hospedajes activos
        hospedajes_activos = self.registros_hospedaje.filter(
            fecha_checkout__isnull=True,
            fecha_checkin__date__lt=fecha_salida,
        ).exists()
        
        if hospedajes_activos:
            return False
        
        return True


# =============================================================================
# FOTOS DE HABITACIÓN (con thumbnails automáticos)
# =============================================================================

class HabitacionFoto(BaseModel):
    """
    Galería de fotos de una habitación.
    Usa django-imagekit para generar thumbnails automáticos.
    
    ¿Por qué no un campo JSON con array de URLs?
    Porque necesitamos: ordenamiento, foto principal, metadatos, optimización.
    """
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.CASCADE,
        related_name='fotos',
        verbose_name="Habitación"
    )
    imagen = models.ImageField(
        upload_to='habitaciones/fotos/%Y/%m/',
        verbose_name="Imagen original"
    )
    # Thumbnail generado AUTOMÁTICAMENTE por imagekit
    thumbnail = ImageSpecField(
        source='imagen',
        processors=[ResizeToFill(400, 300)],
        format='JPEG',
        options={'quality': 85}
    )
    # Versión para tarjetas pequeñas
    miniatura = ImageSpecField(
        source='imagen',
        processors=[ResizeToFill(100, 75)],
        format='JPEG',
        options={'quality': 70}
    )
    orden = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Orden de visualización",
        help_text="Número menor = aparece primero"
    )
    es_principal = models.BooleanField(
        default=False,
        verbose_name="¿Foto principal?",
        help_text="Solo una foto por habitación debe ser principal"
    )

    class Meta:
        verbose_name = "Foto de habitación"
        verbose_name_plural = "Fotos de habitaciones"
        ordering = ['habitacion', 'orden']

    def __str__(self):
        return f"Foto {self.orden} de {self.habitacion}"

    def clean(self):
        """
        Validación: solo UNA foto principal por habitación.
        Este método se ejecuta automáticamente al validar el formulario.
        """
        if self.es_principal:
            # Buscar si ya existe otra foto principal en ESTA habitación
            existente = HabitacionFoto.objects.filter(
                habitacion=self.habitacion,
                es_principal=True
            )
            # Si estamos actualizando, excluirnos a nosotros mismos
            if self.pk:
                existente = existente.exclude(pk=self.pk)
            if existente.exists():
                raise ValidationError({
                    'es_principal': 'Ya existe una foto principal para esta habitación.'
                })

    def save(self, *args, **kwargs):
        # Ejecutar validación antes de guardar
        self.full_clean()
        super().save(*args, **kwargs)


# =============================================================================
# HISTORIAL DE ESTADOS DE HABITACIÓN
# =============================================================================

class EstadoHabitacion(BaseModel):
    """
    Registro HISTÓRICO de estados de una habitación.
    Cada cambio de estado genera un NUEVO registro (append-only).
    
    Hereda de BaseModel para tener:
    - created_at: cuándo se inició este estado
    - updated_at: última modificación del registro
    - activo: soft delete
    """
    
    class Estado(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', '✅ Disponible'
        OCUPADA = 'OCUPADA', '🚫 Ocupada'
        SUCIA = 'SUCIA', '🧹 En Limpieza'
        MANTENIMIENTO = 'MANTENIMIENTO', '🔧 Mantenimiento'
        RESERVADA = 'RESERVADA', '📅 Reservada'

    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.CASCADE,
        related_name='estados',
        verbose_name="Habitación"
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        verbose_name="Estado"
    )
    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        verbose_name="Inicio del estado"
    )
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin del estado",
        help_text="Si está vacío, este es el estado actual"
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas del cambio de estado"
    )

    class Meta:
        verbose_name = "Estado de habitación"
        verbose_name_plural = "Historial de estados"
        ordering = ['-fecha_inicio']
        get_latest_by = 'fecha_inicio'


    def __str__(self):
        estado_display = self.get_estado_display()
        return f"{self.habitacion.codigo} → {estado_display} ({self.fecha_inicio:%d/%m/%Y %H:%M})"

    @property
    def duracion(self):
        """Duración de este estado. Si está vigente, calcula hasta ahora."""
        fin = self.fecha_fin if self.fecha_fin else timezone.now()
        return fin - self.fecha_inicio


# =============================================================================
# HUÉSPED
# =============================================================================

class Huesped(BaseModel):
    """
    Persona que se hospeda o se ha hospedado en el hotel.
    
    ¿Por qué separado de Clientes (que no implementamos aún)?
    Un "Cliente" puede ser una agencia de viajes, una empresa, etc.
    Un "Huésped" es siempre una persona física que duerme en una habitación.
    """
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    documento_identidad = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Documento de identidad",
        help_text="RIF, Pasaporte, Cédula, DNI"
    )
    nacionalidad = models.CharField(
        max_length=100,
        default='Venezolano',
        verbose_name="Nacionalidad"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Correo electrónico"
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono principal"
    )
    telefono_alternativo = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono alternativo"
    )
    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de nacimiento"
    )
    tipo_cliente = models.ForeignKey(
        'usuarios.TipoCliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='huespedes',
        verbose_name="Tipo de Cliente"
    )

    class Meta:
        verbose_name = "Huésped"
        verbose_name_plural = "Huéspedes"
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


# =============================================================================
# REGISTRO DE HOSPEDAJE (Check-in / Check-out)
# =============================================================================

class RegistroHospedaje(BaseModel):
    """
    Registro de una estadía: desde check-in hasta check-out.
    Una habitación puede tener MUCHOS registros a lo largo del tiempo.
    
    REGLA DE NEGOCIO CRÍTICA:
    No puede haber DOS registros activos (sin checkout) para la misma habitación.
    """
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.PROTECT,
        related_name='registros_hospedaje',
        verbose_name="Habitación"
    )
    huesped = models.ForeignKey(
        Huesped,
        on_delete=models.PROTECT,
        related_name='registros_hospedaje',
        verbose_name="Huésped principal"
    )
    fecha_checkin = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha y hora de check-in"
    )
    fecha_checkout = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha y hora de check-out",
        help_text="Vacío = huésped aún en el hotel"
    )
    cantidad_personas = models.PositiveSmallIntegerField(
        verbose_name="Cantidad de personas",
        help_text="Incluyendo al huésped principal"
    )
    tarifa_aplicada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Tarifa por noche",
        help_text="Precio acordado al momento del check-in"
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas del hospedaje"
    )

    cliente = models.ForeignKey(
        'usuarios.Cliente',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='hospedajes',
        verbose_name="Facturar a"
    )

    class Meta:
        verbose_name = "Registro de hospedaje"
        verbose_name_plural = "Registros de hospedaje"
        ordering = ['-fecha_checkin']

    def __str__(self):
        estado = "Activo" if self.esta_activo else "Finalizado"
        return f"{self.huesped} en {self.habitacion.codigo} [{estado}]"

    @property
    def esta_activo(self):
        """Un registro está activo si no tiene fecha de checkout."""
        return self.fecha_checkout is None

    @property
    def noches_estadia(self):
        """Calcula el número de noches (redondea hacia arriba)."""
        fin = self.fecha_checkout if self.fecha_checkout else timezone.now()
        delta = fin - self.fecha_checkin
        # Redondear hacia arriba: 1 día y 3 horas = 2 noches
        import math
        return math.ceil(delta.total_seconds() / 86400)

    @property
    def total_estadia(self):
        """Total a cobrar: noches × tarifa."""
        return self.noches_estadia * self.tarifa_aplicada


    def hacer_checkout(self, notas=''):
        """
        Ejecuta el checkout:
        1. Cierra este registro (fecha_checkout = now)
        2. Cambia la habitación a estado SUCIA (para limpieza)
        """
        with transaction.atomic():
            # 1. Cerrar registro de hospedaje
            self.fecha_checkout = timezone.now()
            self.save(update_fields=['fecha_checkout'])

            # 2. Poner habitación en limpieza
            self.habitacion.cambiar_estado('SUCIA', f'Check-out {self.huesped}. {notas}')

            return self

    def clean(self):
        """
        Validaciones antes de guardar:
        - No permitir check-in si la habitación no está disponible
        - No permitir exceder capacidad máxima
        - No permitir doble check-in activo
        """
        # Solo validar al crear (no al actualizar)
        if not self.pk:
            # ¿Está disponible la habitación?
            if not self.habitacion.esta_disponible:
                raise ValidationError({
                    'habitacion': f'La habitación {self.habitacion.codigo} no está disponible.'
                })

            # ¿Excede capacidad?
            if self.cantidad_personas > self.habitacion.tipo.capacidad_maxima:
                raise ValidationError({
                    'cantidad_personas': f'Capacidad máxima: {self.habitacion.tipo.capacidad_maxima} personas.'
                })

            # ¿Ya tiene un registro activo?
            activo_existente = RegistroHospedaje.objects.filter(
                habitacion=self.habitacion,
                fecha_checkout__isnull=True
            ).exists()
            if activo_existente:
                raise ValidationError({
                    'habitacion': f'La habitación {self.habitacion.codigo} ya tiene un huésped activo.'
                })

    def save(self, *args, **kwargs):
        """
        Al guardar un nuevo registro:
        - Cambia automáticamente el estado de la habitación a OCUPADA
        """
        es_nuevo = self.pk is None

        if es_nuevo:
            # Validar reglas de negocio
            self.full_clean()

        with transaction.atomic():
            # Guardar el registro primero
            if es_nuevo:
                # Forzar insert para nuevo registro
                super().save(*args, **kwargs)
            else:
                super().save(*args, **kwargs)

            # Si es nuevo check-in, cambiar estado de habitación
            if es_nuevo:
                self.habitacion.cambiar_estado(
                    'OCUPADA',
                    f'Check-in: {self.huesped.nombre_completo}'
                )



# =============================================================================
# RESERVA (FASE 2)
# =============================================================================

class Reserva(BaseModel):
    """
    Reserva de una habitación para un rango de fechas.
    
    REGLAS DE NEGOCIO:
    - No puede haber DOS reservas confirmadas que se solapen en la misma habitación.
    - Al hacer check-in, la reserva pasa a estado CONFIRMADA automáticamente.
    - Una reserva puede estar PENDIENTE, CONFIRMADA, CANCELADA o NO_SHOW.
    """

    class EstadoReserva(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        NO_SHOW = 'NO_SHOW', 'No se presentó'

    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name="Habitación"
    )
    huesped = models.ForeignKey(
        Huesped,
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name="Huésped"
    )
    fecha_entrada = models.DateField(verbose_name="Fecha de entrada")
    fecha_salida = models.DateField(verbose_name="Fecha de salida")
    cantidad_personas = models.PositiveSmallIntegerField(default=1)
    estado = models.CharField(
        max_length=20,
        choices=EstadoReserva.choices,
        default=EstadoReserva.PENDIENTE,
        verbose_name="Estado"
    )
    tarifa_por_noche = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Tarifa por noche"
    )
    notas = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['fecha_entrada', 'fecha_salida']

    def __str__(self):
        return f"Reserva {self.huesped} → {self.habitacion.codigo} ({self.fecha_entrada} - {self.fecha_salida})"

    @property
    def noches(self):
        """Calcula el número de noches de la reserva."""
        return (self.fecha_salida - self.fecha_entrada).days

    @property
    def total(self):
        """Total a pagar: noches × tarifa."""
        return self.noches * self.tarifa_por_noche

    def clean(self):
        """Validaciones de reglas de negocio."""
        if self.fecha_entrada >= self.fecha_salida:
            raise ValidationError('La fecha de entrada debe ser anterior a la de salida.')

        if self.cantidad_personas > self.habitacion.tipo.capacidad_maxima:
            raise ValidationError(
                f'Capacidad máxima: {self.habitacion.tipo.capacidad_maxima} personas.'
            )

        # Verificar solapamiento solo para reservas CONFIRMADAS o PENDIENTES
        if self.estado in ['CONFIRMADA', 'PENDIENTE']:
            solapadas = Reserva.objects.filter(
                habitacion=self.habitacion,
                estado__in=['CONFIRMADA', 'PENDIENTE'],
                fecha_entrada__lt=self.fecha_salida,
                fecha_salida__gt=self.fecha_entrada,
            )
            if self.pk:
                solapadas = solapadas.exclude(pk=self.pk)
            if solapadas.exists():
                raise ValidationError(
                    'La habitación ya está reservada en ese rango de fechas.'
                )
            

