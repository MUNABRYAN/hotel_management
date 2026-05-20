"""
Template tags personalizados para el módulo de hotel.
Principio DRY: Estas funciones de presentación se usan en múltiples templates,
así que las centralizamos aquí en lugar de repetir HTML en cada lugar.
"""
from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def badge_estado(estado_str):
    """
    Retorna un badge de Bootstrap con el color correspondiente al estado.
    
    Uso en template:
    {% load hotel_tags %}
    {% badge_estado habitacion.estado_str %}
    """
    ESTILOS = {
        'DISPONIBLE': {
            'bg': 'success',
            'icono': 'check-circle-fill',
            'texto': 'Disponible'
        },
        'OCUPADA': {
            'bg': 'danger',
            'icono': 'door-closed-fill',
            'texto': 'Ocupada'
        },
        'SUCIA': {
            'bg': 'warning text-dark',
            'icono': 'broom',
            'texto': 'En Limpieza'
        },
        'MANTENIMIENTO': {
            'bg': 'secondary',
            'icono': 'tools',
            'texto': 'Mantenimiento'
        },
        'RESERVADA': {
            'bg': 'primary',
            'icono': 'calendar-check-fill',
            'texto': 'Reservada'
        },
    }
    
    estilo = ESTILOS.get(estado_str, {
        'bg': 'dark',
        'icono': 'question-circle-fill',
        'texto': estado_str
    })
    
    return format_html(
        '<span class="badge bg-{}"><i class="bi bi-{} me-1"></i>{}</span>',
        estilo['bg'],
        estilo['icono'],
        estilo['texto']
    )


@register.simple_tag
def tarjeta_estado(estado_str):
    """
    Retorna la clase CSS para el borde de la tarjeta según el estado.
    Las tarjetas del panel cambian de color de borde según el estado.
    
    Uso: <div class="card {% tarjeta_estado habitacion.estado_str %}">
    """
    BORDES = {
        'DISPONIBLE': 'border-success',
        'OCUPADA': 'border-danger',
        'SUCIA': 'border-warning',
        'MANTENIMIENTO': 'border-secondary',
        'RESERVADA': 'border-primary',
    }
    return BORDES.get(estado_str, 'border-dark')


@register.simple_tag
def icono_estado(estado_str):
    """Retorna el ícono de Bootstrap Icons para cada estado."""
    ICONOS = {
        'DISPONIBLE': 'check-circle-fill text-success',
        'OCUPADA': 'door-closed-fill text-danger',
        'SUCIA': 'broom text-warning',
        'MANTENIMIENTO': 'tools text-secondary',
        'RESERVADA': 'calendar-check-fill text-primary',
    }
    return ICONOS.get(estado_str, 'question-circle-fill text-dark')


@register.filter
def multiplicar(valor, factor):
    """Filtro para multiplicar valores en templates. Útil para cálculos simples."""
    try:
        return valor * factor
    except (TypeError, ValueError):
        return ''
    

@register.filter
def get_attr(obj, attr):
    """Obtiene un atributo dinámicamente de un objeto."""
    return getattr(obj, attr, '')

from django import forms

@register.filter
def bootstrap_field(field):
    """
    Renderiza un campo de formulario con clases Bootstrap 5.
    Detecta automáticamente el tipo de campo.
    """
    if not field:
        return ''
    
    # Obtener clases CSS adecuadas
    css_class = 'form-control'
    
    if isinstance(field.field, forms.BooleanField):
        css_class = 'form-check-input'
        widget_html = field.as_widget(attrs={'class': css_class})
        return f'<div class="form-check form-switch mb-3">{widget_html} <label class="form-check-label" for="{field.id_for_label}">{field.label}</label></div>'
    
    if isinstance(field.field, forms.ChoiceField) and not isinstance(field.field, forms.MultipleChoiceField):
        css_class = 'form-select'
    
    if isinstance(field.field, forms.MultipleChoiceField):
        css_class = 'form-select'
    
    if isinstance(field.field.widget, forms.CheckboxSelectMultiple):
        css_class = 'form-check-input'
        widget_html = field.as_widget(attrs={'class': css_class})
        return f'<div class="mb-3"><label class="form-label fw-bold small">{field.label}</label><div class="d-flex flex-wrap gap-2">{widget_html}</div></div>'
    
    # Campo estándar
    attrs = {'class': css_class, 'placeholder': field.label}
    if isinstance(field.field.widget, forms.Textarea):
        attrs['rows'] = 3
    
    widget_html = field.as_widget(attrs=attrs)
    
    required = '<span class="text-danger">*</span>' if field.field.required else ''
    help_text = f'<div class="form-text small">{field.help_text}</div>' if field.help_text else ''
    errors = f'<div class="invalid-feedback d-block">{" ".join(field.errors)}</div>' if field.errors else ''
    
    return f'''
        <div class="mb-3">
            <label for="{field.id_for_label}" class="form-label fw-bold small">{field.label} {required}</label>
            {widget_html}
            {help_text}
            {errors}
        </div>
    '''