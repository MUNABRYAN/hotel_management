"""
Comando de Django para inicializar datos de prueba en el sistema hotelero.
Uso: python manage.py inicializar_datos

PRINCIPIO: Datos de prueba determinísticos y realistas.
Cada ejecución limpia datos anteriores y crea nuevos consistentes.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from hotel.models import (
    Habitacion, TipoHabitacion, HabitacionFoto,
    EstadoHabitacion, Huesped, RegistroHospedaje
)
from core.models import UbicacionHabitacion, CaracteristicaHabitacion
from temporadas.models import TipoTemporada, Temporada, TarifaHabitacion


class Command(BaseCommand):
    help = 'Inicializa el sistema con datos de prueba realistas para un hotel'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🏨 Inicializando datos del hotel...'))
        
        with transaction.atomic():
            # Limpiar datos existentes (hard delete real, no soft delete)
            self.stdout.write('  Limpiando datos anteriores...')
            RegistroHospedaje.todos.all().delete()
            EstadoHabitacion.todos.all().delete()
            HabitacionFoto.todos.all().delete()
            Habitacion.todos.all().delete()
            TipoHabitacion.todos.all().delete()
            CaracteristicaHabitacion.todos.all().delete()
            UbicacionHabitacion.todos.all().delete()
            Huesped.todos.all().delete()  # Hard delete para evitar conflictos de unique

            # 1. UBICACIONES
            self.stdout.write('  Creando ubicaciones...')
            ubicaciones = {
                'torre_a': UbicacionHabitacion.objects.create(
                    nombre='Torre Principal',
                    descripcion='Edificio principal, acceso directo al lobby'
                ),
                'torre_b': UbicacionHabitacion.objects.create(
                    nombre='Torre B - Vista al Mar',
                    descripcion='Torre lateral con balcón y vista panorámica al mar'
                ),
                'jardin': UbicacionHabitacion.objects.create(
                    nombre='Vista al Jardín',
                    descripcion='Habitaciones con vista a los jardines internos'
                ),
            }
            
            # 2. CARACTERÍSTICAS
            self.stdout.write('  Creando características...')
            caracteristicas = {
                'wifi': CaracteristicaHabitacion.objects.create(
                    nombre='WiFi', icono='bi-wifi'
                ),
                'tv': CaracteristicaHabitacion.objects.create(
                    nombre='TV Cable', icono='bi-tv'
                ),
                'jacuzzi': CaracteristicaHabitacion.objects.create(
                    nombre='Jacuzzi', icono='bi-droplet'
                ),
                'minibar': CaracteristicaHabitacion.objects.create(
                    nombre='Minibar', icono='bi-cup'
                ),
                'ac': CaracteristicaHabitacion.objects.create(
                    nombre='Aire Acondicionado', icono='bi-snow'
                ),
                'caja_fuerte': CaracteristicaHabitacion.objects.create(
                    nombre='Caja Fuerte', icono='bi-shield-lock'
                ),
                'room_service': CaracteristicaHabitacion.objects.create(
                    nombre='Room Service 24h', icono='bi-bell'
                ),
                'vista_mar': CaracteristicaHabitacion.objects.create(
                    nombre='Vista al Mar', icono='bi-water'
                ),
            }
            
            # 3. TIPOS DE HABITACIÓN
            self.stdout.write('  Creando tipos de habitación...')
            
            tipo_simple = TipoHabitacion.objects.create(
                nombre='Habitación Simple',
                capacidad_maxima=1,
                descripcion='Ideal para viajeros individuales. Cama individual, baño privado.'
            )
            tipo_simple.caracteristicas.add(
                caracteristicas['wifi'], caracteristicas['tv'], caracteristicas['ac']
            )
            
            tipo_doble = TipoHabitacion.objects.create(
                nombre='Habitación Doble',
                capacidad_maxima=2,
                descripcion='Cama matrimonial o dos camas individuales. Perfecta para parejas.'
            )
            tipo_doble.caracteristicas.add(
                caracteristicas['wifi'], caracteristicas['tv'],
                caracteristicas['ac'], caracteristicas['minibar']
            )
            
            tipo_suite = TipoHabitacion.objects.create(
                nombre='Suite Junior',
                capacidad_maxima=3,
                descripcion='Sala de estar separada, jacuzzi, vista panorámica.'
            )
            tipo_suite.caracteristicas.add(
                caracteristicas['wifi'], caracteristicas['tv'],
                caracteristicas['jacuzzi'], caracteristicas['minibar'],
                caracteristicas['ac'], caracteristicas['caja_fuerte'],
                caracteristicas['room_service']
            )
            
            tipo_presidencial = TipoHabitacion.objects.create(
                nombre='Suite Presidencial',
                capacidad_maxima=4,
                descripcion='Máximo lujo. Dos habitaciones, sala, comedor, jacuzzi, terraza privada.'
            )
            tipo_presidencial.caracteristicas.add(
                caracteristicas['wifi'], caracteristicas['tv'],
                caracteristicas['jacuzzi'], caracteristicas['minibar'],
                caracteristicas['ac'], caracteristicas['caja_fuerte'],
                caracteristicas['room_service'], caracteristicas['vista_mar']
            )
            
            # 4. HABITACIONES
            self.stdout.write('  Creando habitaciones...')
            
            # Piso 1 - Habitaciones Simples y Dobles
            habitaciones_piso1 = []
            for i in range(101, 106):
                tipo = tipo_simple if i <= 103 else tipo_doble
                hab = Habitacion.objects.create(
                    codigo=str(i),
                    nombre=f'Habitación {i}',
                    tipo=tipo,
                    ubicacion=ubicaciones['torre_a'],
                    piso=1,
                    extension_telefono=f'10{i}'
                )
                hab.cambiar_estado('DISPONIBLE', 'Habitación lista para uso')
                habitaciones_piso1.append(hab)
            
            # Piso 2 - Habitaciones Dobles y Suites
            habitaciones_piso2 = []
            for i in range(201, 205):
                tipo = tipo_doble if i <= 203 else tipo_suite
                hab = Habitacion.objects.create(
                    codigo=str(i),
                    nombre=f'{tipo.nombre} {i}',
                    tipo=tipo,
                    ubicacion=ubicaciones['torre_a'],
                    piso=2,
                    extension_telefono=f'20{i}'
                )
                hab.cambiar_estado('DISPONIBLE', 'Habitación lista para uso')
                habitaciones_piso2.append(hab)
            
            # Piso 3 - Suites y Presidencial
            habitaciones_piso3 = []
            for i in range(301, 304):
                tipo = tipo_suite if i <= 302 else tipo_presidencial
                ubicacion = ubicaciones['torre_b'] if i == 301 else ubicaciones['jardin']
                hab = Habitacion.objects.create(
                    codigo=str(i),
                    nombre=f'{tipo.nombre} {i}',
                    tipo=tipo,
                    ubicacion=ubicacion,
                    piso=3,
                    extension_telefono=f'30{i}'
                )
                hab.cambiar_estado('DISPONIBLE', 'Habitación lista para uso')
                habitaciones_piso3.append(hab)
            
            # Habitación 304 en mantenimiento
            hab_mantenimiento = Habitacion.objects.create(
                codigo='304',
                nombre='Suite Imperial 304',
                tipo=tipo_suite,
                ubicacion=ubicaciones['torre_b'],
                piso=3,
                extension_telefono='304',
                notas_internas='Aire acondicionado en reparación. No asignar hasta nuevo aviso.'
            )
            hab_mantenimiento.cambiar_estado('MANTENIMIENTO', 'Reparación de aire acondicionado')
            
            # 5. HUÉSPEDES
            self.stdout.write('  Creando huéspedes de prueba...')
            
            huespedes = [
                Huesped.objects.create(
                    nombres='María Elena',
                    apellidos='González Pérez',
                    documento_identidad='V12345678',
                    nacionalidad='Venezolana',
                    email='maria.gonzalez@email.com',
                    telefono='04141234567',
                    fecha_nacimiento='1990-05-15'
                ),
                Huesped.objects.create(
                    nombres='John Michael',
                    apellidos='Smith',
                    documento_identidad='P98765432',
                    nacionalidad='Estadounidense',
                    email='john.smith@email.com',
                    telefono='04149876543',
                    fecha_nacimiento='1985-11-20'
                ),
                Huesped.objects.create(
                    nombres='Carlos Alberto',
                    apellidos='Rodríguez Martínez',
                    documento_identidad='V23456789',
                    nacionalidad='Venezolano',
                    email='carlos.rodriguez@email.com',
                    telefono='04241234567',
                    fecha_nacimiento='1978-03-08'
                ),
                Huesped.objects.create(
                    nombres='Ana Sofía',
                    apellidos='López Castillo',
                    documento_identidad='V34567890',
                    nacionalidad='Venezolana',
                    email='ana.lopez@email.com',
                    telefono='04161234567',
                    fecha_nacimiento='1995-07-22'
                ),
            ]
            
            # 6. CHECK-INS ACTIVOS
            self.stdout.write('  Creando check-ins activos...')
            
            # María en habitación 101
            hab_101 = Habitacion.objects.get(codigo='101')
            RegistroHospedaje.objects.create(
                habitacion=hab_101,
                huesped=huespedes[0],
                cantidad_personas=1,
                tarifa_aplicada=75.00
            )
            
            # John y Ana (pareja) en habitación 202
            hab_202 = Habitacion.objects.get(codigo='202')
            RegistroHospedaje.objects.create(
                habitacion=hab_202,
                huesped=huespedes[1],
                cantidad_personas=2,
                tarifa_aplicada=120.00
            )
            
            # Carlos en suite 301
            hab_301 = Habitacion.objects.get(codigo='301')
            RegistroHospedaje.objects.create(
                habitacion=hab_301,
                huesped=huespedes[2],
                cantidad_personas=2,
                tarifa_aplicada=250.00
            )
            
            # 7. CHECK-OUTS DE AYER (para historial)
            self.stdout.write('  Creando check-outs históricos...')
            ayer = timezone.now() - timezone.timedelta(days=1)
            
            registro_historico = RegistroHospedaje.objects.create(
                habitacion=Habitacion.objects.get(codigo='103'),
                huesped=huespedes[3],
                cantidad_personas=1,
                tarifa_aplicada=75.00,
                fecha_checkin=ayer - timezone.timedelta(days=2),
                fecha_checkout=ayer
            )
            # Actualizar estado de esa habitación
            hab_103 = Habitacion.objects.get(codigo='103')
            hab_103.cambiar_estado('SUCIA', f'Check-out {huespedes[3].nombre_completo}')


            # 8. TEMPORADAS Y TARIFAS (FASE 2)
            self.stdout.write('  Creando temporadas y tarifas...')

            tipo_alta = TipoTemporada.objects.create(
                nombre='Temporada Alta',
                color='#dc3545',
                descripcion='Julio-Agosto y Diciembre'
            )
            tipo_baja = TipoTemporada.objects.create(
                nombre='Temporada Baja',
                color='#198754',
                descripcion='Resto del año'
            )
            tipo_festivo = TipoTemporada.objects.create(
                nombre='Festivos',
                color='#ffc107',
                descripcion='Carnaval, Semana Santa, Navidad'
            )

            # Crear temporadas para 2026
            Temporada.objects.create(
                tipo=tipo_alta,
                nombre='Verano 2026',
                fecha_inicio='2026-07-01',
                fecha_fin='2026-08-31',
                año=2026
            )
            Temporada.objects.create(
                tipo=tipo_festivo,
                nombre='Navidad 2026',
                fecha_inicio='2026-12-20',
                fecha_fin='2026-12-31',
                año=2026
            )
            Temporada.objects.create(
                tipo=tipo_baja,
                nombre='Baja Mayo 2026',
                fecha_inicio='2026-05-01',
                fecha_fin='2026-05-31',
                año=2026
            )

            # Tarifas por tipo de habitación y temporada
            tipos_habitacion = TipoHabitacion.objects.all()
            for th in tipos_habitacion:
                if th.nombre == 'Habitación Simple':
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_alta, precio_por_noche=90)
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_baja, precio_por_noche=60)
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_festivo, precio_por_noche=110)
                elif th.nombre == 'Habitación Doble':
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_alta, precio_por_noche=140)
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_baja, precio_por_noche=90)
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_festivo, precio_por_noche=170)
                elif th.nombre == 'Suite Junior':
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_alta, precio_por_noche=250)
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_baja, precio_por_noche=160)
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_festivo, precio_por_noche=300)
                else:
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_alta, precio_por_noche=400)
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_baja, precio_por_noche=280)
                    TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_festivo, precio_por_noche=500)



        # RESUMEN
        self.stdout.write(self.style.SUCCESS('\n✅ DATOS INICIALIZADOS EXITOSAMENTE'))
        self.stdout.write(f'   Ubicaciones: {UbicacionHabitacion.objects.count()}')
        self.stdout.write(f'   Características: {CaracteristicaHabitacion.objects.count()}')
        self.stdout.write(f'   Tipos de habitación: {TipoHabitacion.objects.count()}')
        self.stdout.write(f'   Habitaciones: {Habitacion.objects.count()}')
        self.stdout.write(f'   Huéspedes: {Huesped.objects.count()}')
        self.stdout.write(f'   Check-ins activos: {RegistroHospedaje.objects.filter(fecha_checkout__isnull=True).count()}')