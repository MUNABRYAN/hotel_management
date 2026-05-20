"""
Vistas principales del módulo de hotel.
FASE 1: Dashboard, Panel de Habitaciones, Detalle de Habitación.

PRINCIPIO: Vistas basadas en clases (CBV) con Mixins de Django.
Las vistas son "tontas" - la lógica de negocio vive en los modelos.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from datetime import datetime, date
from temporadas.models import Temporada, TarifaHabitacion
from django.views.decorators.http import require_POST
from datetime import timedelta

from django.views.generic import ListView as LV
from .forms import HabitacionForm, HabitacionFotoFormSet

# Importar TODOS los modelos necesarios
from .models import (
    Habitacion,
    TipoHabitacion,
    HabitacionFoto,
    EstadoHabitacion,
    Huesped,
    RegistroHospedaje,
    Reserva
)
import json


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Panel principal del sistema.
    Muestra conteo de habitaciones por estado y últimos check-ins.
    """
    template_name = 'hotel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        habitaciones = Habitacion.objects.select_related('tipo', 'ubicacion')
        
        total = habitaciones.count()
        disponibles = sum(1 for h in habitaciones if h.esta_disponible)
        ocupadas = sum(1 for h in habitaciones if h.esta_ocupada)
        
        context['total_habitaciones'] = total
        context['habitaciones_disponibles'] = disponibles
        context['habitaciones_ocupadas'] = ocupadas
        context['habitaciones_otros'] = total - disponibles - ocupadas
        
        hoy = timezone.now().date()
        context['checkins_hoy'] = RegistroHospedaje.objects.filter(
            fecha_checkin__date=hoy
        ).select_related('habitacion', 'huesped').order_by('-fecha_checkin')[:10]
        
        context['hospedajes_activos'] = RegistroHospedaje.objects.filter(
            fecha_checkout__isnull=True
        ).select_related('habitacion', 'huesped').order_by('fecha_checkin')
        
        return context


class PanelHabitacionesView(LoginRequiredMixin, ListView):
    """
    Vista tipo GRID que muestra habitaciones agrupadas por piso.
    Incluye filtros por estado vía JavaScript.
    """
    model = Habitacion
    template_name = 'hotel/panel_habitaciones.html'
    context_object_name = 'habitaciones'
    
    def get_queryset(self):
        """Optimización: select_related + prefetch_related para evitar N+1 queries."""
        return Habitacion.objects.select_related(
            'tipo', 'ubicacion'
        ).prefetch_related(
            'fotos',
            'estados'
        ).all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agrupar habitaciones por piso
        habitaciones = self.get_queryset()
        pisos = {}
        for hab in habitaciones:
            if hab.piso not in pisos:
                pisos[hab.piso] = []
            pisos[hab.piso].append(hab)
        
        # Ordenar pisos numéricamente
        context['habitaciones_por_piso'] = dict(sorted(pisos.items()))
        
        # Estados disponibles para filtros
        context['estados_disponibles'] = EstadoHabitacion.Estado.choices
        
        return context


class DetalleHabitacionView(LoginRequiredMixin, DetailView):
    """
    Vista de detalle de una habitación.
    Muestra fotos, características, huésped actual e historial de estados.
    """
    model = Habitacion
    template_name = 'hotel/detalle_habitacion.html'
    context_object_name = 'habitacion'
    
    def get_queryset(self):
        """Optimizar consultas para el detalle."""
        return Habitacion.objects.select_related(
            'tipo', 'ubicacion'
        ).prefetch_related(
            'fotos',
            'tipo__caracteristicas',
            'estados',
            'registros_hospedaje__huesped'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Últimos 10 cambios de estado
        context['historial_estados'] = self.object.estados.all()[:10]
        
        # Hospedaje activo (si la habitación está ocupada)
        context['hospedaje_activo'] = self.object.registros_hospedaje.filter(
            fecha_checkout__isnull=True
        ).select_related('huesped').first()
        
        return context

# =============================================================================
# VISTAS DE ACCIÓN: Cambios de estado, Check-in, Check-out
# PRINCIPIO DRY: Una sola vista maneja TODOS los cambios de estado.
# La lógica específica de check-in/check-out se delega a métodos separados.
# =============================================================================

class CambiarEstadoHabitacionView(LoginRequiredMixin, View):
    """
    Vista genérica para cambiar el estado de una habitación.
    
    MANEJA:
    - Cambios simples: DISPONIBLE → SUCIA → DISPONIBLE
    - Check-in: DISPONIBLE → OCUPADA (requiere datos de huésped)
    - Check-out: OCUPADA → SUCIA (cierra el registro de hospedaje)
    
    ¿Por qué una sola vista y no 4?
    DRY: El patrón es idéntico en todos los casos:
    1. Recibir habitación_id + acción
    2. Validar que la acción sea válida
    3. Ejecutar cambio atómico
    4. Redirigir con mensaje
    
    Solo check-in/out tienen lógica ADICIONAL que se maneja con métodos separados.
    """
    
    ACCIONES_SIMPLES = ['limpiar', 'mantenimiento', 'disponible', 'reservar']
    
    def post(self, request, pk):
        """
        Procesa la solicitud de cambio de estado.
        
        Args:
            request: HttpRequest con datos del formulario
            pk: ID de la habitación
        
        Returns:
            HttpResponseRedirect al panel de habitaciones
        """
        habitacion = get_object_or_404(Habitacion, pk=pk)
        accion = request.POST.get('accion', '')
        notas = request.POST.get('notas', '')
        
        # Mapeo de acciones a estados
        MAPEO_ESTADOS = {
            'limpiar': 'SUCIA',
            'mantenimiento': 'MANTENIMIENTO',
            'disponible': 'DISPONIBLE',
            'reservar': 'RESERVADA',
        }
        
        try:
            if accion in self.ACCIONES_SIMPLES:
                # Cambio simple de estado
                nuevo_estado = MAPEO_ESTADOS[accion]
                habitacion.cambiar_estado(nuevo_estado, notas)
                messages.success(
                    request,
                    f'Habitación {habitacion.codigo}: {habitacion.estado_actual.get_estado_display()}'
                )
                
            elif accion == 'checkin':
                # Check-in: requiere datos adicionales del huésped
                return self._procesar_checkin(request, habitacion)
                
            elif accion == 'checkout':
                # Check-out: cierra el hospedaje activo
                return self._procesar_checkout(request, habitacion)
                
            else:
                messages.error(request, f'Acción no reconocida: {accion}')
                
        except ValidationError as e:
            # Capturar errores de validación del modelo
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f'Error: {error}')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
        
        # Redirigir al panel (o a la página anterior si existe)
        next_url = request.POST.get('next', '')
        if next_url:
            return redirect(next_url)
        return redirect('hotel:panel_habitaciones')
    
    def _procesar_checkin(self, request, habitacion):
        """
        Lógica específica de check-in.
        
        Validaciones (además de las del modelo):
        - La habitación debe estar DISPONIBLE
        - Debe proporcionarse ID de huésped o datos para crear uno nuevo
        """
        # Obtener datos del formulario
        huesped_id = request.POST.get('huesped_id')
        cantidad_personas = int(request.POST.get('cantidad_personas', 1))
        tarifa = request.POST.get('tarifa', 0)
        notas_checkin = request.POST.get('notas_checkin', '')
        
        # Validar que la habitación está disponible
        if not habitacion.esta_disponible:
            messages.error(
                request,
                f'La habitación {habitacion.codigo} no está disponible. '
                f'Estado actual: {habitacion.estado_str}'
            )
            return redirect('hotel:panel_habitaciones')
        
        # Buscar o validar huésped
        try:
            if huesped_id:
                huesped = get_object_or_404(Huesped, pk=huesped_id)
                # Cliente para facturación
                cliente_id = request.POST.get('cliente_id')
                cliente = None
                if cliente_id:
                    from usuarios.models import Cliente
                    cliente = get_object_or_404(Cliente, pk=cliente_id)
            else:
                # Si no se proporciona ID, redirigir a crear huésped primero
                messages.warning(request, 'Debe seleccionar un huésped para el check-in.')
                return redirect('hotel:panel_habitaciones')
            
            # Crear registro de hospedaje (el modelo valida automáticamente)
            registro = RegistroHospedaje.objects.create(
                habitacion=habitacion,
                huesped=huesped,
                cantidad_personas=cantidad_personas,
                tarifa_aplicada=tarifa,
                notas=notas_checkin,
                cliente=cliente,  
            )
            
            messages.success(
                request,
                f'✅ Check-in exitoso: {huesped.nombre_completo} en {habitacion.codigo}'
            )
            
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f'Error de validación: {error}')
        except Exception as e:
            messages.error(request, f'Error al procesar check-in: {str(e)}')
        
        return redirect('hotel:panel_habitaciones')
    
    def _procesar_checkout(self, request, habitacion):
        """
        Lógica específica de check-out.
        
        Busca el registro de hospedaje activo y lo cierra.
        El modelo RegistroHospedaje.hacer_checkout() ya maneja:
        - Cerrar el registro (fecha_checkout = now)
        - Cambiar estado de habitación a SUCIA
        """
        registro_activo = RegistroHospedaje.objects.filter(
            habitacion=habitacion,
            fecha_checkout__isnull=True
        ).first()
        
        if not registro_activo:
            messages.error(
                request,
                f'La habitación {habitacion.codigo} no tiene un huésped activo para hacer check-out.'
            )
            return redirect('hotel:panel_habitaciones')
        
        try:
            registro_activo.hacer_checkout()
            total = registro_activo.total_estadia
            noches = registro_activo.noches_estadia
            
            messages.success(
                request,
                f'✅ Check-out exitoso: {registro_activo.huesped.nombre_completo} '
                f'({noches} noches - Total: ${total:.2f})'
            )
        except Exception as e:
            messages.error(request, f'Error al procesar check-out: {str(e)}')
        
        return redirect('hotel:panel_habitaciones')    
    

class ListaHuespedesAPI(LoginRequiredMixin, View):
    """
    Endpoint temporal para obtener lista de huéspedes en JSON.
    FASE 2: Migrar a Django REST Framework con ViewSet completo.
    """
    def get(self, request):
        huespedes = Huesped.objects.values(
            'id', 'nombres', 'apellidos', 'documento_identidad'
        ).order_by('apellidos')[:50]  # Limitar a 50 para rendimiento
        
        # Formatear respuesta
        resultado = []
        for h in huespedes:
            resultado.append({
                'id': h['id'],
                'nombre_completo': f"{h['nombres']} {h['apellidos']}",
                'documento_identidad': h['documento_identidad'],
            })
        
        return JsonResponse(resultado, safe=False)

class CrearHuespedAPI(LoginRequiredMixin, View):
    """
    Endpoint para crear un nuevo huésped vía AJAX.
    FASE 2: Migrar a Django REST Framework con serializer completo.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validar campos requeridos
            campos_requeridos = ['nombres', 'apellidos', 'documento_identidad', 'telefono']
            for campo in campos_requeridos:
                if not data.get(campo):
                    return JsonResponse({
                        'error': f'El campo {campo} es obligatorio'
                    }, status=400)
            
            # Verificar documento duplicado
            if Huesped.objects.filter(documento_identidad=data['documento_identidad']).exists():
                return JsonResponse({
                    'error': 'Ya existe un huésped con ese documento de identidad'
                }, status=400)
            
            # Crear huésped
            huesped = Huesped.objects.create(
                nombres=data['nombres'],
                apellidos=data['apellidos'],
                documento_identidad=data['documento_identidad'],
                nacionalidad=data.get('nacionalidad', 'Venezolano'),
                telefono=data['telefono'],
                email=data.get('email', ''),
            )
            
            return JsonResponse({
                'id': huesped.id,
                'nombre_completo': huesped.nombre_completo,
                'documento_identidad': huesped.documento_identidad,
                'mensaje': 'Huésped creado exitosamente'
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

class CrearHuespedAPI(LoginRequiredMixin, View):
    """
    Endpoint para crear un nuevo huésped vía AJAX.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validar campos requeridos
            if not data.get('nombres'):
                return JsonResponse({'error': 'El campo Nombres es obligatorio'}, status=400)
            if not data.get('apellidos'):
                return JsonResponse({'error': 'El campo Apellidos es obligatorio'}, status=400)
            if not data.get('documento_identidad'):
                return JsonResponse({'error': 'El campo Documento de Identidad es obligatorio'}, status=400)
            if not data.get('telefono'):
                return JsonResponse({'error': 'El campo Teléfono es obligatorio'}, status=400)
            
            # Verificar documento duplicado
            if Huesped.objects.filter(documento_identidad=data['documento_identidad']).exists():
                return JsonResponse({
                    'error': 'Ya existe un huésped con ese documento de identidad'
                }, status=400)
            
            # Crear huésped
            huesped = Huesped.objects.create(
                nombres=data['nombres'],
                apellidos=data['apellidos'],
                documento_identidad=data['documento_identidad'],
                nacionalidad=data.get('nacionalidad', 'Venezolano'),
                telefono=data['telefono'],
                email=data.get('email', ''),
            )
            
            return JsonResponse({
                'id': huesped.id,
                'nombre_completo': huesped.nombre_completo,
                'documento_identidad': huesped.documento_identidad,
                'mensaje': 'Huésped creado exitosamente'
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)        
        

class CrearHabitacionView(LoginRequiredMixin, CreateView):
    """
    Formulario para crear una nueva habitación desde la interfaz.
    Solo administradores y gerentes.
    """
    model = Habitacion
    template_name = 'hotel/form_habitacion.html'
    fields = [
        'codigo', 'nombre', 'tipo', 'ubicacion',
        'extension_telefono', 'piso', 'notas_internas'
    ]
    success_url = reverse_lazy('hotel:panel_habitaciones')
    
    def form_valid(self, form):
        """Al crear la habitación, asignar estado DISPONIBLE automáticamente."""
        response = super().form_valid(form)
        self.object.cambiar_estado('DISPONIBLE', 'Habitación recién creada')
        messages.success(
            self.request,
            f'✅ Habitación {self.object.codigo} creada y lista para uso.'
        )
        return response
    

class DisponibilidadAPI(LoginRequiredMixin, View):
    """
    Endpoint que devuelve habitaciones disponibles en un rango de fechas.
    GET /hotel/api/disponibilidad/?entrada=2026-06-01&salida=2026-06-05&tipo=2
    """
    def get(self, request):
        entrada_str = request.GET.get('entrada')
        salida_str = request.GET.get('salida')
        tipo_id = request.GET.get('tipo')
        
        if not entrada_str or not salida_str:
            return JsonResponse({'error': 'Fechas requeridas'}, status=400)
        
        try:
            entrada = datetime.strptime(entrada_str, '%Y-%m-%d').date()
            salida = datetime.strptime(salida_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Formato de fecha: YYYY-MM-DD'}, status=400)
        
        if entrada >= salida:
            return JsonResponse({'error': 'Entrada debe ser anterior a salida'}, status=400)
        
        # Filtrar habitaciones
        habitaciones = Habitacion.objects.select_related('tipo', 'ubicacion')
        if tipo_id:
            habitaciones = habitaciones.filter(tipo_id=tipo_id)
        
        # Buscar temporada para la fecha de entrada
        temporada_activa = Temporada.obtener_temporada_activa(entrada)
        
        disponibles = []
        for hab in habitaciones:
            if hab.disponible_en_fechas(entrada, salida):
                tarifa = None
                nombre_temporada = None
                
                if temporada_activa:
                    tarifa_obj = TarifaHabitacion.objects.filter(
                        tipo_habitacion=hab.tipo,
                        tipo_temporada=temporada_activa.tipo
                    ).first()
                    if tarifa_obj:
                        tarifa = float(tarifa_obj.precio_por_noche)
                        nombre_temporada = temporada_activa.tipo.nombre
                
                disponibles.append({
                    'id': hab.id,
                    'codigo': hab.codigo,
                    'tipo': hab.tipo.nombre,
                    'tipo_id': hab.tipo_id,
                    'capacidad': hab.tipo.capacidad_maxima,
                    'piso': hab.piso,
                    'ubicacion': hab.ubicacion.nombre,
                    'tarifa_por_noche': tarifa,
                    'temporada': nombre_temporada,
                })
        
        return JsonResponse({
            'disponibles': disponibles,
            'total': len(disponibles),
            'temporada_activa': temporada_activa.nombre if temporada_activa else 'No definida',
        })    

class CrearReservaAPI(LoginRequiredMixin, View):
    """
    Endpoint para crear una reserva vía AJAX.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            habitacion_id = data.get('habitacion_id')
            huesped_id = data.get('huesped_id')
            fecha_entrada_str = data.get('fecha_entrada')
            fecha_salida_str = data.get('fecha_salida')
            cantidad_personas = int(data.get('cantidad_personas', 1))
            tarifa = float(data.get('tarifa', 0))
            notas = data.get('notas', '')
            
            # Validar campos requeridos
            if not all([habitacion_id, huesped_id, fecha_entrada_str, fecha_salida_str]):
                return JsonResponse({'error': 'Todos los campos son requeridos'}, status=400)
            
            habitacion = get_object_or_404(Habitacion, pk=habitacion_id)
            huesped = get_object_or_404(Huesped, pk=huesped_id)
            fecha_entrada = datetime.strptime(fecha_entrada_str, '%Y-%m-%d').date()
            fecha_salida = datetime.strptime(fecha_salida_str, '%Y-%m-%d').date()
            
            # Crear reserva (las validaciones están en model.clean())
            reserva = Reserva.objects.create(
                habitacion=habitacion,
                huesped=huesped,
                fecha_entrada=fecha_entrada,
                fecha_salida=fecha_salida,
                cantidad_personas=cantidad_personas,
                tarifa_por_noche=tarifa,
                estado='CONFIRMADA',
                notas=notas
            )
            
            return JsonResponse({
                'id': reserva.id,
                'mensaje': f'Reserva confirmada: {huesped.nombre_completo} en {habitacion.codigo}',
                'noches': reserva.noches,
                'total': float(reserva.total),
            }, status=201)
            
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class BuscarDisponibilidadView(LoginRequiredMixin, TemplateView):
    """
    Vista para buscar habitaciones disponibles por tipo y fechas.
    """
    template_name = 'hotel/buscar_disponibilidad.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_habitacion'] = TipoHabitacion.objects.filter(activo=True)
        return context

class HabitacionesOcupadasAPI(LoginRequiredMixin, View):
    """Devuelve habitaciones ocupadas con su huésped activo."""
    def get(self, request):
        registros = RegistroHospedaje.objects.filter(
            fecha_checkout__isnull=True
        ).select_related('habitacion', 'huesped')
        
        data = []
        for r in registros:
            data.append({
                'hospedaje_id': r.id,
                'codigo': r.habitacion.codigo,
                'huesped': r.huesped.nombre_completo,
                'noches': r.noches_estadia,
                'total_actual': float(r.total_estadia),
            })
        return JsonResponse(data, safe=False)


class ProductosAPI(LoginRequiredMixin, View):
    """Devuelve lista de productos disponibles."""
    def get(self, request):
        from restaurant.models import Producto
        productos = Producto.objects.filter(disponible=True, activo=True).select_related('grupo')
        data = []
        for p in productos:
            data.append({
                'id': p.id,
                'codigo': p.codigo,
                'descripcion': p.descripcion,
                'grupo': p.grupo.nombre,
                'precio_publico': float(p.precio_publico),
                'precio_huesped': float(p.precio_huesped),
            })
        return JsonResponse(data, safe=False)


class CargarConsumoAPI(LoginRequiredMixin, View):
    """Carga un consumo a la cuenta de un huésped."""
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            registro = get_object_or_404(RegistroHospedaje, pk=data['registro_hospedaje_id'])
            from restaurant.models import Producto, ConsumoHabitacion
            producto = get_object_or_404(Producto, pk=data['producto_id'])
            
            consumo = ConsumoHabitacion.objects.create(
                registro_hospedaje=registro,
                producto=producto,
                cantidad=int(data.get('cantidad', 1)),
                precio_unitario=float(data.get('precio_unitario', 0)),
            )
            
            return JsonResponse({
                'id': consumo.id,
                'mensaje': f'{producto.descripcion} cargado a Hab. {registro.habitacion.codigo}',
                'subtotal': float(consumo.subtotal),
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class CargosHabitacionView(LoginRequiredMixin, TemplateView):
    template_name = 'hotel/cargos_habitacion.html'

    
class CalendarioEventosAPI(LoginRequiredMixin, View):
    """
    Endpoint que devuelve reservas y temporadas en formato FullCalendar.
    GET /hotel/api/calendario-eventos/?start=2026-05-01&end=2026-06-30
    """
    def get(self, request):
        from datetime import datetime
        start_raw = request.GET.get('start', '')
        end_raw = request.GET.get('end', '')

        # FullCalendar envía formato ISO con timezone: "2026-04-26T00:00:00-04:00"
        # Extraemos solo la fecha YYYY-MM-DD
        start_str = start_raw[:10] if start_raw else ''
        end_str = end_raw[:10] if end_raw else ''
        
        eventos = []
        
        # RESERVAS
        reservas = Reserva.objects.filter(
            estado__in=['CONFIRMADA', 'PENDIENTE'],
            activo=True
        ).select_related('habitacion', 'huesped')
        
        if start_str:
            reservas = reservas.filter(fecha_salida__gte=start_str)
        if end_str:
            reservas = reservas.filter(fecha_entrada__lte=end_str)
        
        for r in reservas:
            eventos.append({
                'id': f'reserva_{r.id}',
                'title': f'{r.huesped.nombre_completo} - Hab. {r.habitacion.codigo}',
                'start': r.fecha_entrada.isoformat(),
                'end': (r.fecha_salida + timedelta(days=1)).isoformat(),
                'backgroundColor': '#0d6efd',
                'borderColor': '#0d6efd',
                'textColor': '#fff',
                'extendedProps': {
                    'tipo': 'reserva',
                    'habitacion': r.habitacion.codigo,
                    'huesped': r.huesped.nombre_completo,
                    'noches': r.noches,
                    'total': float(r.total),
                    'estado': r.estado,
                }
            })
        
        # TEMPORADAS
        temporadas = Temporada.objects.filter(activo=True).select_related('tipo')
        
        if start_str:
            temporadas = temporadas.filter(fecha_fin__gte=start_str)
        if end_str:
            temporadas = temporadas.filter(fecha_inicio__lte=end_str)
        
        for t in temporadas:
            eventos.append({
                'id': f'temporada_{t.id}',
                'title': t.tipo.nombre,
                'start': t.fecha_inicio.isoformat(),
                'end': (t.fecha_fin + timedelta(days=1)).isoformat(),
                'backgroundColor': t.tipo.color,
                'borderColor': t.tipo.color,
                'textColor': '#000' if t.tipo.color == '#ffc107' else '#fff',
                'display': 'background',
                'extendedProps': {
                    'tipo': 'temporada',
                    'nombre': t.nombre,
                }
            })
        
        # CHECK-INS ACTIVOS
        hospedajes = RegistroHospedaje.objects.filter(
            fecha_checkout__isnull=True,
            activo=True
        ).select_related('habitacion', 'huesped')
        
        for h in hospedajes:
            hoy = timezone.now().date()
            eventos.append({
                'id': f'checkin_{h.id}',
                'title': f'🟢 {h.huesped.nombre_completo} - Hab. {h.habitacion.codigo}',
                'start': hoy.isoformat(),
                'end': (hoy + timedelta(days=1)).isoformat(),
                'backgroundColor': '#dc3545',
                'borderColor': '#dc3545',
                'textColor': '#fff',
                'extendedProps': {
                    'tipo': 'checkin',
                    'habitacion': h.habitacion.codigo,
                    'huesped': h.huesped.nombre_completo,
                }
            })
        
        return JsonResponse(eventos, safe=False)            
    
class CalendarioView(LoginRequiredMixin, TemplateView):
    template_name = 'hotel/calendario.html'
    

class HabitacionListView(LoginRequiredMixin, LV):
    model = Habitacion
    template_name = 'hotel/crud_habitacion_list.html'
    context_object_name = 'habitaciones'
    ordering = ['piso', 'codigo']


class HabitacionCreateView(LoginRequiredMixin, CreateView):
    model = Habitacion
    form_class = HabitacionForm
    template_name = 'hotel/crud_habitacion_form.html'
    success_url = reverse_lazy('hotel:crud_habitacion_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['fotos_formset'] = HabitacionFotoFormSet(self.request.POST, self.request.FILES)
        else:
            context['fotos_formset'] = HabitacionFotoFormSet()
        context['modo'] = 'Nueva'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        fotos_formset = context['fotos_formset']
        self.object = form.save()
        if fotos_formset.is_valid():
            fotos_formset.instance = self.object
            fotos_formset.save()
        # Crear estado inicial
        self.object.cambiar_estado('DISPONIBLE', 'Habitación creada')
        messages.success(self.request, f'Habitación {self.object.codigo} creada.')
        return redirect(self.success_url)


class HabitacionUpdateView(LoginRequiredMixin, UpdateView):
    model = Habitacion
    form_class = HabitacionForm
    template_name = 'hotel/crud_habitacion_form.html'
    success_url = reverse_lazy('hotel:crud_habitacion_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['fotos_formset'] = HabitacionFotoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['fotos_formset'] = HabitacionFotoFormSet(instance=self.object)
        context['modo'] = 'Editar'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        fotos_formset = context['fotos_formset']
        self.object = form.save()
        if fotos_formset.is_valid():
            fotos_formset.instance = self.object
            fotos_formset.save()
        messages.success(self.request, f'Habitación {self.object.codigo} actualizada.')
        return redirect(self.success_url)


class HabitacionDeleteView(LoginRequiredMixin, DeleteView):
    model = Habitacion
    template_name = 'core/generic_confirm_delete.html'
    success_url = reverse_lazy('hotel:crud_habitacion_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = {
            'titulo_plural': 'Habitaciones',
            'titulo_singular': 'Habitación',
            'success_url': self.success_url,
        }
        return context

    def form_valid(self, form):
        obj = self.get_object()
        messages.warning(self.request, f'Habitación {obj.codigo} eliminada.')
        return super().form_valid(form)
    

class ClientesAPI(LoginRequiredMixin, View):
    def get(self, request):
        from usuarios.models import Cliente
        clientes = Cliente.objects.filter(activo=True).order_by('nombre')
        data = [{'id': c.id, 'nombre': c.nombre, 'tipo': c.tipo, 'rif': c.rif} for c in clientes]
        return JsonResponse(data, safe=False)