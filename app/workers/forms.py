from django import forms
# Importamos el mixin de estilos desde core
from core.forms import ColoredFormMixin

from .models import Trabajador, JornadaLaboral, TrabajadorJornada

class TrabajadorForm(ColoredFormMixin, forms.ModelForm):
    class Meta:
        color_scheme = 'indigo'
        model = Trabajador
        fields = [
            'numero_empleado', 'activo',
            'nombre', 'apellido_paterno', 'apellido_materno',
            'rfc', 'curp', 'email',
            'unidad', 'puesto', 'tipo_nombramiento'
        ]

class JornadaLaboralForm(ColoredFormMixin, forms.ModelForm):
    class Meta:
        color_scheme = 'teal'
        model = JornadaLaboral
        fields = ['descripcion', 'hora_entrada', 'hora_salida', 'dias_semana']
        widgets = {
            'hora_entrada': forms.TimeInput(attrs={
                'type': 'time',
                'style': 'padding-left: 2.5rem;'  
            }),
            'hora_salida': forms.TimeInput(attrs={
                'type': 'time',
                'style': 'padding-left: 2.5rem;'  
            }),
        }
        help_texts = {
            'dias_semana': 'Formato sugerido: Lunes a Viernes'
        }    

class AsignarJornadaForm(ColoredFormMixin, forms.ModelForm):
    class Meta:
        color_scheme = 'cyan'
        model = TrabajadorJornada
        fields = ['trabajador', 'jornada', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        # Validar que fecha_inicio no sea None
        if not fecha_inicio:
            self.add_error("fecha_inicio", "Debe seleccionar una fecha de inicio.")
            return cleaned_data

        # Validar que fecha_fin no sea menor a fecha_inicio
        if fecha_fin and fecha_fin < fecha_inicio:
            self.add_error("fecha_fin", "La fecha de fin no puede ser menor que la fecha de inicio.")

        return cleaned_data
