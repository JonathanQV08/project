from django import forms
from core.models import CalendarioLaboral
from core.forms import ColoredFormMixin
from .models import RegistroAsistencia


class AsistenciaAdminForm(ColoredFormMixin, forms.ModelForm):
    """
    Formulario para ADMIN y JEFE.
    Permite editar trabajador, fecha, entrada/salida e incidencia.
    """
    class Meta:
        color_scheme = 'rose'
        model = RegistroAsistencia
        fields = ['trabajador', 'fecha', 'hora_entrada', 'hora_salida', 'incidencia']

        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_entrada': forms.TimeInput(attrs={'type': 'time'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time'}),
        }




class AsistenciaTrabajadorForm(ColoredFormMixin, forms.ModelForm):
    """
    Formulario simplificado para TRABAJADOR.
    No permite elegir trabajador ni fecha.
    Solo registra su entrada/salida.
    """
    class Meta:
        color_scheme = 'indigo'
        model = RegistroAsistencia
        fields = ['hora_entrada', 'hora_salida']

        widgets = {
            'hora_entrada': forms.TimeInput(attrs={'type': 'time'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        data = super().clean()
        h_ent = data.get('hora_entrada')
        h_sal = data.get('hora_salida')

        # Validación básica
        if h_ent and h_sal and h_sal <= h_ent:
            raise forms.ValidationError("La hora de salida debe ser posterior a la hora de entrada.")

        return data
