"""
Comando de Django para inicializar datos de prueba en el sistema hotelero.
Uso: python manage.py inicializar_datos

PRINCIPIO: Datos de prueba determinísticos y realistas.
Cada ejecución limpia datos anteriores y crea nuevos consistentes.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import time, date, timedelta

from core.models import UbicacionHabitacion, CaracteristicaHabitacion, PisoSeccion
from hotel.models import (
    Habitacion, TipoHabitacion, HabitacionFoto,
    EstadoHabitacion, Huesped, RegistroHospedaje, Reserva
)
from usuarios.models import (
    Cargo, Turno, Empleado, TipoCliente, Cliente, UsuarioPersonalizado
)
from temporadas.models import TipoTemporada, Temporada, TarifaHabitacion
from restaurant.models import GrupoProducto, Producto, MenuDelDia, MenuItem, ConsumoHabitacion


class Command(BaseCommand):
    help = 'Inicializa el sistema con datos de prueba realistas para un hotel'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🏨 Inicializando datos del hotel...'))
        
        with transaction.atomic():
            # ============================================================
            # LIMPIEZA TOTAL (hard delete)
            # ============================================================
            self.stdout.write('  Limpiando datos anteriores...')
            ConsumoHabitacion.todos.all().delete()
            MenuItem.objects.all().delete()
            MenuDelDia.objects.all().delete()
            Producto.todos.all().delete()
            GrupoProducto.todos.all().delete()
            TarifaHabitacion.todos.all().delete()
            Temporada.todos.all().delete()
            TipoTemporada.todos.all().delete()
            Reserva.todos.all().delete()
            RegistroHospedaje.todos.all().delete()
            EstadoHabitacion.todos.all().delete()
            HabitacionFoto.todos.all().delete()
            Habitacion.todos.all().delete()
            TipoHabitacion.todos.all().delete()
            CaracteristicaHabitacion.todos.all().delete()
            UbicacionHabitacion.todos.all().delete()
            PisoSeccion.todos.all().delete()
            Huesped.todos.all().delete()
            Cliente.todos.all().delete()
            TipoCliente.todos.all().delete()
            Empleado.todos.all().delete()
            Turno.todos.all().delete()
            Cargo.todos.all().delete()

            # ============================================================
            # 1. UBICACIONES
            # ============================================================
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

            # ============================================================
            # 1.5 PISOS / SECCIONES
            # ============================================================
            self.stdout.write('  Creando pisos/secciones...')
            p1 = PisoSeccion.objects.create(nombre='Piso 1', tipo='PISO', orden=1)
            p2 = PisoSeccion.objects.create(nombre='Piso 2', tipo='PISO', orden=2)
            p3 = PisoSeccion.objects.create(nombre='Piso 3', tipo='PISO', orden=3)

            # ============================================================
            # 2. CARACTERÍSTICAS
            # ============================================================
            self.stdout.write('  Creando características...')
            caracteristicas = {
                'wifi': CaracteristicaHabitacion.objects.create(nombre='WiFi', icono='bi-wifi'),
                'tv': CaracteristicaHabitacion.objects.create(nombre='TV Cable', icono='bi-tv'),
                'jacuzzi': CaracteristicaHabitacion.objects.create(nombre='Jacuzzi', icono='bi-droplet'),
                'minibar': CaracteristicaHabitacion.objects.create(nombre='Minibar', icono='bi-cup'),
                'ac': CaracteristicaHabitacion.objects.create(nombre='Aire Acondicionado', icono='bi-snow'),
                'caja_fuerte': CaracteristicaHabitacion.objects.create(nombre='Caja Fuerte', icono='bi-shield-lock'),
                'room_service': CaracteristicaHabitacion.objects.create(nombre='Room Service 24h', icono='bi-bell'),
                'vista_mar': CaracteristicaHabitacion.objects.create(nombre='Vista al Mar', icono='bi-water'),
            }

            # ============================================================
            # 3. TIPOS DE HABITACIÓN
            # ============================================================
            self.stdout.write('  Creando tipos de habitación...')
            tipo_simple = TipoHabitacion.objects.create(
                nombre='Habitación Simple', capacidad_maxima=1,
                descripcion='Ideal para viajeros individuales. Cama individual, baño privado.'
            )
            tipo_simple.caracteristicas.add(caracteristicas['wifi'], caracteristicas['tv'], caracteristicas['ac'])

            tipo_doble = TipoHabitacion.objects.create(
                nombre='Habitación Doble', capacidad_maxima=2,
                descripcion='Cama matrimonial o dos camas individuales. Perfecta para parejas.'
            )
            tipo_doble.caracteristicas.add(
                caracteristicas['wifi'], caracteristicas['tv'],
                caracteristicas['ac'], caracteristicas['minibar']
            )

            tipo_suite = TipoHabitacion.objects.create(
                nombre='Suite Junior', capacidad_maxima=3,
                descripcion='Sala de estar separada, jacuzzi, vista panorámica.'
            )
            tipo_suite.caracteristicas.add(
                caracteristicas['wifi'], caracteristicas['tv'], caracteristicas['jacuzzi'],
                caracteristicas['minibar'], caracteristicas['ac'], caracteristicas['caja_fuerte'],
                caracteristicas['room_service']
            )

            tipo_presidencial = TipoHabitacion.objects.create(
                nombre='Suite Presidencial', capacidad_maxima=4,
                descripcion='Máximo lujo. Dos habitaciones, sala, comedor, jacuzzi, terraza privada.'
            )
            tipo_presidencial.caracteristicas.add(
                caracteristicas['wifi'], caracteristicas['tv'], caracteristicas['jacuzzi'],
                caracteristicas['minibar'], caracteristicas['ac'], caracteristicas['caja_fuerte'],
                caracteristicas['room_service'], caracteristicas['vista_mar']
            )

            # ============================================================
            # 4. HABITACIONES
            # ============================================================
            self.stdout.write('  Creando habitaciones...')
            # Piso 1
            for i in range(101, 106):
                tipo = tipo_simple if i <= 103 else tipo_doble
                hab = Habitacion.objects.create(
                    codigo=str(i), nombre=f'Habitación {i}',
                    tipo=tipo, ubicacion=ubicaciones['torre_a'],
                    piso_seccion=p1, extension_telefono=f'10{i}'
                )
                hab.cambiar_estado('DISPONIBLE', 'Habitación lista para uso')

            # Piso 2
            for i in range(201, 205):
                tipo = tipo_doble if i <= 203 else tipo_suite
                hab = Habitacion.objects.create(
                    codigo=str(i), nombre=f'{tipo.nombre} {i}',
                    tipo=tipo, ubicacion=ubicaciones['torre_a'],
                    piso_seccion=p2, extension_telefono=f'20{i}'
                )
                hab.cambiar_estado('DISPONIBLE', 'Habitación lista para uso')

            # Piso 3
            for i in range(301, 304):
                tipo = tipo_suite if i <= 302 else tipo_presidencial
                ubicacion = ubicaciones['torre_b'] if i == 301 else ubicaciones['jardin']
                hab = Habitacion.objects.create(
                    codigo=str(i), nombre=f'{tipo.nombre} {i}',
                    tipo=tipo, ubicacion=ubicacion,
                    piso_seccion=p3, extension_telefono=f'30{i}'
                )
                hab.cambiar_estado('DISPONIBLE', 'Habitación lista para uso')

            # Habitación en mantenimiento
            hab_mant = Habitacion.objects.create(
                codigo='304', nombre='Suite Imperial 304',
                tipo=tipo_suite, ubicacion=ubicaciones['torre_b'],
                piso_seccion=p3, extension_telefono='304',
                notas_internas='Aire acondicionado en reparación. No asignar hasta nuevo aviso.'
            )
            hab_mant.cambiar_estado('MANTENIMIENTO', 'Reparación de aire acondicionado')

            # ============================================================
            # 5. HUÉSPEDES
            # ============================================================
            self.stdout.write('  Creando huéspedes...')
            huespedes = [
                Huesped.objects.create(
                    nombres='María Elena', apellidos='González Pérez',
                    documento_identidad='V12345678', nacionalidad='Venezolana',
                    email='maria.gonzalez@email.com', telefono='04141234567',
                    fecha_nacimiento='1990-05-15'
                ),
                Huesped.objects.create(
                    nombres='John Michael', apellidos='Smith',
                    documento_identidad='P98765432', nacionalidad='Estadounidense',
                    email='john.smith@email.com', telefono='04149876543',
                    fecha_nacimiento='1985-11-20'
                ),
                Huesped.objects.create(
                    nombres='Carlos Alberto', apellidos='Rodríguez Martínez',
                    documento_identidad='V23456789', nacionalidad='Venezolano',
                    email='carlos.rodriguez@email.com', telefono='04241234567',
                    fecha_nacimiento='1978-03-08'
                ),
                Huesped.objects.create(
                    nombres='Ana Sofía', apellidos='López Castillo',
                    documento_identidad='V34567890', nacionalidad='Venezolana',
                    email='ana.lopez@email.com', telefono='04161234567',
                    fecha_nacimiento='1995-07-22'
                ),
            ]

            # ============================================================
            # 6. TIPOS DE CLIENTE
            # ============================================================
            self.stdout.write('  Creando tipos de cliente...')
            tipo_habitual = TipoCliente.objects.create(
                nombre='Habitual', descripcion='Cliente frecuente',
                descuento=5, color='#0d6efd'
            )
            tipo_vip = TipoCliente.objects.create(
                nombre='VIP', descripcion='Cliente VIP',
                descuento=15, color='#ffc107'
            )
            tipo_turista = TipoCliente.objects.create(
                nombre='Turista', descripcion='Turista ocasional',
                descuento=0, color='#198754'
            )
            tipo_corp = TipoCliente.objects.create(
                nombre='Corporativo', descripcion='Cliente empresarial',
                descuento=10, color='#6c757d'
            )

            # ============================================================
            # 7. CLIENTES (Facturación)
            # ============================================================
            self.stdout.write('  Creando clientes...')
            Cliente.objects.create(
                tipo='NATURAL', rif='V12345678',
                nombre='María Elena González Pérez',
                telefono='04141234567', email='maria.gonzalez@email.com',
                tipo_cliente=tipo_vip
            )
            Cliente.objects.create(
                tipo='JURIDICO', rif='J-123456789',
                nombre='Corporación Smith, C.A.',
                direccion_fiscal='Av. Principal, Centro Empresarial, Piso 5',
                telefono='02121234567', email='facturacion@smith.com',
                tipo_cliente=tipo_corp
            )

            # ============================================================
            # 8. CHECK-INS ACTIVOS
            # ============================================================
            self.stdout.write('  Creando check-ins activos...')
            hab_101 = Habitacion.objects.get(codigo='101')
            RegistroHospedaje.objects.create(
                habitacion=hab_101, huesped=huespedes[0],
                cantidad_personas=1, tarifa_aplicada=60.00
            )

            hab_202 = Habitacion.objects.get(codigo='202')
            RegistroHospedaje.objects.create(
                habitacion=hab_202, huesped=huespedes[1],
                cantidad_personas=2, tarifa_aplicada=90.00
            )

            hab_301 = Habitacion.objects.get(codigo='301')
            RegistroHospedaje.objects.create(
                habitacion=hab_301, huesped=huespedes[2],
                cantidad_personas=2, tarifa_aplicada=160.00
            )

            # Check-out histórico
            ayer = timezone.now() - timedelta(days=1)
            RegistroHospedaje.objects.create(
                habitacion=Habitacion.objects.get(codigo='103'),
                huesped=huespedes[3], cantidad_personas=1,
                tarifa_aplicada=60.00,
                fecha_checkin=ayer - timedelta(days=2),
                fecha_checkout=ayer
            )
            Habitacion.objects.get(codigo='103').cambiar_estado('SUCIA', f'Check-out {huespedes[3].nombre_completo}')

            # ============================================================
            # 9. RESERVAS
            # ============================================================
            self.stdout.write('  Creando reservas...')
            hoy = timezone.now().date()
            Reserva.objects.create(
                habitacion=Habitacion.objects.get(codigo='104'),
                huesped=huespedes[0], fecha_entrada=hoy + timedelta(days=3),
                fecha_salida=hoy + timedelta(days=6),
                cantidad_personas=2, tarifa_por_noche=90.00,
                estado='CONFIRMADA', notas='Llegada tarde, preparar cena fría'
            )
            Reserva.objects.create(
                habitacion=Habitacion.objects.get(codigo='302'),
                huesped=huespedes[1], fecha_entrada=hoy + timedelta(days=7),
                fecha_salida=hoy + timedelta(days=10),
                cantidad_personas=3, tarifa_por_noche=160.00,
                estado='CONFIRMADA'
            )

            # ============================================================
            # 10. TEMPORADAS Y TARIFAS
            # ============================================================
            self.stdout.write('  Creando temporadas y tarifas...')
            tipo_alta = TipoTemporada.objects.create(nombre='Temporada Alta', color='#dc3545')
            tipo_baja = TipoTemporada.objects.create(nombre='Temporada Baja', color='#198754')
            tipo_festivo = TipoTemporada.objects.create(nombre='Festivos', color='#ffc107')

            Temporada.objects.create(tipo=tipo_baja, nombre='Baja Todo 2026',
                                     fecha_inicio='2026-01-01', fecha_fin='2026-12-31', año=2026)
            Temporada.objects.create(tipo=tipo_baja, nombre='Baja Mayo 2026',
                                     fecha_inicio='2026-05-01', fecha_fin='2026-05-31', año=2026)
            Temporada.objects.create(tipo=tipo_alta, nombre='Verano 2026',
                                     fecha_inicio='2026-07-01', fecha_fin='2026-08-31', año=2026)
            Temporada.objects.create(tipo=tipo_festivo, nombre='Navidad 2026',
                                     fecha_inicio='2026-12-20', fecha_fin='2026-12-31', año=2026)

            tarifas = {
                'Habitación Simple': (60, 90, 110),
                'Habitación Doble': (90, 140, 170),
                'Suite Junior': (160, 250, 300),
                'Suite Presidencial': (280, 400, 500),
            }
            for th in TipoHabitacion.objects.all():
                baja, alta, festivo = tarifas[th.nombre]
                TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_baja, precio_por_noche=baja)
                TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_alta, precio_por_noche=alta)
                TarifaHabitacion.objects.create(tipo_habitacion=th, tipo_temporada=tipo_festivo, precio_por_noche=festivo)

            # ============================================================
            # 11. RESTAURANT - Grupos y Productos
            # ============================================================
            self.stdout.write('  Creando productos del restaurant...')
            bebidas = GrupoProducto.objects.create(nombre='Bebidas', aplicacion='AMBOS')
            entradas = GrupoProducto.objects.create(nombre='Entradas', aplicacion='RESTAURANT')
            platos = GrupoProducto.objects.create(nombre='Platos Fuertes', aplicacion='RESTAURANT')
            postres = GrupoProducto.objects.create(nombre='Postres', aplicacion='RESTAURANT')
            licores = GrupoProducto.objects.create(nombre='Licores', aplicacion='AMBOS')
            servicios = GrupoProducto.objects.create(nombre='Servicios', aplicacion='HOTEL')

            productos_data = [
                ('P001', 'Cerveza Nacional', bebidas, 3.50, 3.00, 2.50),
                ('P002', 'Refresco Lata', bebidas, 2.00, 1.80, 1.50),
                ('P003', 'Agua Mineral', bebidas, 1.50, 1.20, 1.00),
                ('P004', 'Coctel Especial', licores, 12.00, 10.00, 8.00),
                ('P005', 'Whisky 12 años', licores, 25.00, 22.00, 18.00),
                ('P006', 'Ensalada César', entradas, 8.00, 7.00, 6.00),
                ('P007', 'Sopa del Día', entradas, 6.00, 5.00, 4.50),
                ('P008', 'Parrilla Mixta', platos, 22.00, 20.00, 16.00),
                ('P009', 'Pescado del Día', platos, 18.00, 16.00, 14.00),
                ('P010', 'Torta de Chocolate', postres, 7.00, 6.00, 5.00),
                ('P011', 'Lavandería', servicios, 10.00, 10.00, 8.00),
                ('P012', 'Room Service (cargo)', servicios, 5.00, 5.00, 3.00),
            ]
            for codigo, desc, grupo, pub, huesp, per in productos_data:
                Producto.objects.create(
                    codigo=codigo, descripcion=desc, grupo=grupo,
                    precio_publico=pub, precio_huesped=huesp, precio_personal=per
                )

            # ============================================================
            # 12. MENÚ DEL DÍA
            # ============================================================
            self.stdout.write('  Creando menú del día...')
            menu = MenuDelDia.objects.create(
                nombre='Menú Ejecutivo', fecha=hoy, precio=25.00, disponible=True
            )
            MenuItem.objects.create(menu=menu, producto=Producto.objects.get(codigo='P006'), categoria='ENTRADA')
            MenuItem.objects.create(menu=menu, producto=Producto.objects.get(codigo='P007'), categoria='SOPA')
            MenuItem.objects.create(menu=menu, producto=Producto.objects.get(codigo='P008'), categoria='PLATO')
            MenuItem.objects.create(menu=menu, producto=Producto.objects.get(codigo='P010'), categoria='POSTRE')
            MenuItem.objects.create(menu=menu, producto=Producto.objects.get(codigo='P002'), categoria='BEBIDA')

            # ============================================================
            # 13. CONSUMOS A HABITACIÓN
            # ============================================================
            self.stdout.write('  Creando consumos de prueba...')
            reg_101 = RegistroHospedaje.objects.filter(habitacion__codigo='101', fecha_checkout__isnull=True).first()
            if reg_101:
                ConsumoHabitacion.objects.create(
                    registro_hospedaje=reg_101,
                    producto=Producto.objects.get(codigo='P004'),
                    cantidad=2, precio_unitario=10.00
                )
                ConsumoHabitacion.objects.create(
                    registro_hospedaje=reg_101,
                    producto=Producto.objects.get(codigo='P011'),
                    cantidad=1, precio_unitario=10.00
                )

            # ============================================================
            # 14. CARGOS Y TURNOS
            # ============================================================
            self.stdout.write('  Creando cargos y turnos...')
            gerente = Cargo.objects.create(nombre='Gerente General')
            recepcionista = Cargo.objects.create(nombre='Recepcionista')
            camarero = Cargo.objects.create(nombre='Camarero')
            botones = Cargo.objects.create(nombre='Botones')
            ama_llaves = Cargo.objects.create(nombre='Ama de Llaves')
            chef = Cargo.objects.create(nombre='Chef')

            turno_manana = Turno.objects.create(nombre='Mañana', hora_inicio=time(7,0), hora_fin=time(15,0), color='#ffc107')
            turno_tarde = Turno.objects.create(nombre='Tarde', hora_inicio=time(15,0), hora_fin=time(23,0), color='#fd7e14')
            turno_noche = Turno.objects.create(nombre='Noche', hora_inicio=time(23,0), hora_fin=time(7,0), color='#6f42c1')

            # ============================================================
            # 15. EMPLEADOS
            # ============================================================
            self.stdout.write('  Creando empleados...')
            Empleado.objects.create(
                cedula='V10000001', nombres='Luis', apellidos='Martínez',
                cargo=gerente, turno=turno_manana, celular='04141111111',
                fecha_ingreso='2024-01-15'
            )
            Empleado.objects.create(
                cedula='V10000002', nombres='Carmen', apellidos='Rodríguez',
                cargo=recepcionista, turno=turno_tarde, celular='04142222222',
                fecha_ingreso='2024-03-01'
            )
            Empleado.objects.create(
                cedula='V10000003', nombres='Pedro', apellidos='Sánchez',
                cargo=camarero, turno=turno_manana, celular='04143333333',
                fecha_ingreso='2025-01-10'
            )

        # ============================================================
        # RESUMEN
        # ============================================================
        self.stdout.write(self.style.SUCCESS('\n✅ DATOS INICIALIZADOS EXITOSAMENTE'))
        self.stdout.write(f'   Ubicaciones: {UbicacionHabitacion.objects.count()}')
        self.stdout.write(f'   Pisos/Secciones: {PisoSeccion.objects.count()}')
        self.stdout.write(f'   Características: {CaracteristicaHabitacion.objects.count()}')
        self.stdout.write(f'   Tipos de habitación: {TipoHabitacion.objects.count()}')
        self.stdout.write(f'   Habitaciones: {Habitacion.objects.count()}')
        self.stdout.write(f'   Huéspedes: {Huesped.objects.count()}')
        self.stdout.write(f'   Clientes: {Cliente.objects.count()}')
        self.stdout.write(f'   Check-ins activos: {RegistroHospedaje.objects.filter(fecha_checkout__isnull=True).count()}')
        self.stdout.write(f'   Reservas: {Reserva.objects.count()}')
        self.stdout.write(f'   Temporadas: {Temporada.objects.count()}')
        self.stdout.write(f'   Tarifas: {TarifaHabitacion.objects.count()}')
        self.stdout.write(f'   Productos: {Producto.objects.count()}')
        self.stdout.write(f'   Menús del día: {MenuDelDia.objects.count()}')
        self.stdout.write(f'   Consumos: {ConsumoHabitacion.objects.count()}')
        self.stdout.write(f'   Cargos: {Cargo.objects.count()}')
        self.stdout.write(f'   Turnos: {Turno.objects.count()}')
        self.stdout.write(f'   Empleados: {Empleado.objects.count()}')