from django import forms
from .models import Habitacion, HabitacionFoto
from core.forms import LocalizedModelForm


class HabitacionForm(LocalizedModelForm):
    class Meta:
        model = Habitacion
        fields = ['codigo', 'nombre', 'tipo', 'ubicacion', 'piso', 'extension_telefono', 'notas_internas']


class HabitacionFotoForm(forms.ModelForm):
    class Meta:
        model = HabitacionFoto
        fields = ['imagen', 'es_principal', 'orden']


# Formset para múltiples fotos
HabitacionFotoFormSet = forms.inlineformset_factory(
    Habitacion, HabitacionFoto,
    form=HabitacionFotoForm,
    extra=4,
    can_delete=True
)