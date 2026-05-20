from django import forms
from django.db import models as django_models


class LocalizedModelForm(forms.ModelForm):
    """
    ModelForm base que aplica localize=True a todos los DecimalField.
    Así Django recibe "1.234,56" y lo convierte a 1234.56 automáticamente.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            model_field = self._meta.model._meta.get_field(field_name)
            if isinstance(model_field, django_models.DecimalField):
                field.localize = True
                field.widget.attrs['class'] = 'form-control'