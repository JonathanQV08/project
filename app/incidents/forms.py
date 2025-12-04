# incidents/forms.py
# Formularios para incidencias

from django import forms
from core.forms import ColoredFormMixin
from .models import Incidencia


class IncidenciaTrabajadorForm(ColoredFormMixin, forms.ModelForm):
    """
    Formulario para que el trabajador capture su incidencia.
    No elige trabajador ni estatus.
    """
    class Meta:
        color_scheme = 'amber'
        model = Incidencia
        fields = [
            'tipo',
            'fecha_inicio',
            'fecha_fin',
            'motivo',
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        data = super().clean()
        fi = data.get('fecha_inicio')
        ff = data.get('fecha_fin')

        if fi and ff and ff < fi:
            self.add_error('fecha_fin', 'La fecha final no puede ser menor a la fecha de inicio.')

        return data


class IncidenciaAdminForm(ColoredFormMixin, forms.ModelForm):
    """
    Formulario para Admin / Jefe.
    Permite elegir trabajador y estatus.
    """
    class Meta:
        color_scheme = 'rose'
        model = Incidencia
        fields = [
            'trabajador',
            'tipo',
            'fecha_inicio',
            'fecha_fin',
            'motivo',
            'estatus',
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        data = super().clean()
        fi = data.get('fecha_inicio')
        ff = data.get('fecha_fin')

        if fi and ff and ff < fi:
            self.add_error('fecha_fin', 'La fecha final no puede ser menor a la fecha de inicio.')

        return data
