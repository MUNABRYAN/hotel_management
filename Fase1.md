
PROMPT COMPLETO PARA LA FASE 1 - FUNDACIÓN HOTEL
markdown
[CONTEXTO GENERAL]
Eres un Arquitecto de Software Senior especializado en Python/Django con 20 años de experiencia construyendo sistemas empresariales. Tu misión es guiarme paso a paso en la construcción de la FASE 1 de un Sistema de Gestión Hotelera. Soy nuevo en Django, así que cada paso debe ser explicado con claridad, justificando decisiones de diseño y mostrando código completo listo para ejecutar.

---

[TECNOLOGÍAS OBLIGATORIAS]
- Backend: Python 3.12, Django 5.0.14, Django REST Framework (para futuras fases con AJAX)
- Frontend: Bootstrap 5.3, FullCalendar.js (para calendario de habitaciones)
- Base de datos: PostgreSQL 16 (producción) / SQLite (desarrollo local)
- Manejo de imágenes: Pillow + django-imagekit (thumbnails automáticos)

---

[PRINCIPIOS DE DISEÑO NO NEGOCIABLES]
1. DRY extremo: Si una lógica se repite 2 veces, se abstrae. Si se repite 3, se crea un Mixin/Manager/Template Tag.
2. Modelos normalizados: Nada de campos como "Precio1, Precio2, Precio3". Eso es un modelo aparte con ForeignKey.
3. Soft Delete: Nada de eliminar registros. Todo tiene campo `activo = BooleanField(default=True)` y un Manager personalizado que filtre por defecto.
4. Timestamps automáticos: Todo modelo hereda de un `BaseModel` con `created_at` y `updated_at`.
5. Vistas basadas en clases (CBV): Nada de funciones-vista gigantes. Usamos ListView, CreateView, UpdateView con Mixins personalizados.
6. Métodos de modelo para lógica de negocio: `habitacion.esta_disponible(fecha)` es un método del modelo, no un if en la vista.

---

[FASE 1 - REQUERIMIENTOS EXACTOS]

### 1. ESTRUCTURA DEL PROYECTO
Crear proyecto Django llamado `hotel_management` con 3 apps iniciales:
- `core`: Modelos base, Mixins, Managers personalizados, templatetags globales
- `hotel`: Gestión de habitaciones, estados, check-in/out
- `usuarios`: Modelo User personalizado (hereda de AbstractUser) con roles: Admin, Recepcionista, Gerente

### 2. MODELOS A IMPLEMENTAR (SOLO FASE 1)

#### 2.1 App `core`
**BaseModel** (Abstracto):
- `created_at`: DateTimeField auto_now_add
- `updated_at`: DateTimeField auto_now
- `activo`: BooleanField default=True

**SoftDeleteManager**: Manager que filtra `activo=True` por defecto

**UbicacionHabitacion**:
- `nombre`: CharField(100) unique
- `descripcion`: TextField blank

**CaracteristicaHabitacion**:
- `nombre`: CharField(100) unique
- `icono`: CharField(50) help_text="Clase de Font Awesome ej: fa-wifi"

#### 2.2 App `hotel`
**TipoHabitacion**:
- `nombre`: CharField(100) unique
- `capacidad_maxima`: PositiveSmallIntegerField
- `descripcion`: TextField
- `caracteristicas`: ManyToManyField(CaracteristicaHabitacion)

**Habitacion**:
- `codigo`: CharField(10) unique
- `nombre`: CharField(100)
- `tipo`: ForeignKey(TipoHabitacion, PROTECT)
- `ubicacion`: ForeignKey(UbicacionHabitacion, PROTECT)
- `extension_telefono`: CharField(10) blank
- `piso`: PositiveSmallIntegerField
- `notas_internas`: TextField blank (solo visible para empleados)

**HabitacionFoto** (para las 4+ fotos por habitación):
- `habitacion`: ForeignKey(Habitacion, related_name='fotos')
- `imagen`: ImageField con thumbnail automático
- `orden`: PositiveSmallIntegerField (para ordenar las fotos)
- `es_principal`: BooleanField(default=False)
- Método para asegurar solo una foto principal por habitación

**EstadoHabitacion** (Historial de estados):
- ESTADOS = [('DISPONIBLE', 'Disponible'), ('OCUPADA', 'Ocupada'), ('SUCIA', 'En Limpieza'), ('MANTENIMIENTO', 'Mantenimiento'), ('RESERVADA', 'Reservada')]
- `habitacion`: ForeignKey(Habitacion, related_name='estados')
- `estado`: CharField(choices=ESTADOS)
- `fecha_inicio`: DateTimeField
- `fecha_fin`: DateTimeField null (si null, el estado sigue vigente)
- `notas`: TextField blank

**Huesped** (Cliente que se hospeda):
- `nombres`, `apellidos`: CharField
- `documento_identidad`: CharField(50) unique (RIF/Pasaporte)
- `nacionalidad`: CharField(100)
- `email`: EmailField blank
- `telefono`: CharField(20)
- `fecha_nacimiento`: DateField null

**RegistroHospedaje** (Check-in/Check-out):
- `habitacion`: ForeignKey(Habitacion, PROTECT)
- `huesped`: ForeignKey(Huesped, PROTECT)
- `fecha_checkin`: DateTimeField
- `fecha_checkout`: DateTimeField null
- `cantidad_personas`: PositiveSmallIntegerField
- `tarifa_aplicada`: DecimalField(max_digits=10, decimal_places=2)
- `notas`: TextField blank
- Método `calcular_total()` que sume noches * tarifa
- Método `checkout()` que cierre el registro y cambie estado de habitación

#### 2.3 App `usuarios`
**UsuarioPersonalizado** (hereda AbstractUser):
- `rol`: CharField(choices=[('ADMIN','Admin'), ('RECEPCION','Recepción'), ('GERENTE','Gerente')])
- `foto`: ImageField
- `telefono`: CharField

### 3. VISTAS Y TEMPLATES (PRIORIDAD UI/UX)

#### 3.1 Dashboard Principal (`/`)
- Tarjetas con conteos: Habitaciones disponibles/ocupadas/sucias
- Lista de últimos check-ins del día
- Calendario semanal con colores por estado (usar FullCalendar.js)
- Esta vista debe cargarse en < 500ms (usar annotate y select_related)

#### 3.2 CRUD Habitaciones (`/hotel/habitaciones/`)
- ListView con DataTable Bootstrap: filtro por tipo, ubicación, estado actual
- CreateView/UpdateView con Form que permita:
  - Subir múltiples fotos con preview (usar Dropzone.js o similar)
  - Seleccionar tipo y ubicación
  - Marcar foto principal
- DeleteView lógica (soft delete: cambia activo=False)

#### 3.3 Panel Visual de Habitaciones (`/hotel/panel/`)
- Vista tipo "grid" de tarjetas por piso
- Cada tarjeta muestra: foto principal, código, estado (con badge de color)
- Click en tarjeta: Modal con detalle completo, fotos en carrusel, historial de estados
- Botones rápidos: Check-in, Marcar Limpieza, Mantenimiento

#### 3.4 Check-in Rápido (`/hotel/checkin/`)
- Buscador de huésped existente (AJAX autocomplete)
- Si no existe: formulario para crear nuevo en el mismo modal
- Seleccionar habitación disponible (mostrar solo DISPONIBLE)
- Asignar tarifa y cantidad de personas
- Al confirmar: crear RegistroHospedaje + cambiar EstadoHabitacion a OCUPADA

### 4. INTERFAZ DE USUARIO (ESTRICTAMENTE BOOTSTRAP 5.3)

#### 4.1 Layout Base
- Sidebar lateral oscuro con iconos (Dashboard, Habitaciones, Panel, Check-in)
- Navbar superior con: buscador global, notificaciones, avatar del usuario
- Footer con estado de conexión (último ping al servidor)

#### 4.2 Componentes Reutilizables
- `badge_estado`: Template tag que retorna badge Bootstrap según estado
- `modal_confirmacion`: Include template para diálogos de confirmación
- `form_field`: Include template que renderiza campos con etiquetas y errores consistentes
- `foto_carrusel`: Include para galería de habitación

### 5. LÓGICA DE NEGOCIO CRÍTICA

#### 5.1 Disponibilidad de Habitación
```python
# En modelo Habitacion:
def estado_actual(self):
    return self.estados.filter(fecha_fin__isnull=True).first()

@property
def esta_disponible(self):
    estado = self.estado_actual()
    return estado and estado.estado == 'DISPONIBLE'
5.2 Check-in
Validar que habitación esté DISPONIBLE

Crear EstadoHabitacion OCUPADA con fecha_inicio = now

Crear RegistroHospedaje

Todo en una transacción atómica (@transaction.atomic)

5.3 Check-out
Cerrar RegistroHospedaje (fecha_checkout = now)

Cambiar estado a SUCIA (para que servicio de limpieza lo vea)

Calcular total de estadía

6. REQUISITOS TÉCNICOS
6.1 Seguridad
CSRF en todos los forms

Escapado XSS en templates

Nunca raw SQL (solo ORM)

Vistas protegidas con LoginRequiredMixin y UserPassesTestMixin por rol

Decorador @receptionist_required para vistas de check-in

6.2 Optimización
select_related para ForeignKey en ListViews

prefetch_related para ManyToMany y reverse FK

Thumbnails automáticos con django-imagekit (nunca cargar imagen full-size en listados)

Paginación de 25 elementos en listados

6.3 Testing
Tests unitarios para métodos de modelo (disponibilidad, checkout)

Tests de integración para checkout flow

Factory Boy para datos de prueba

