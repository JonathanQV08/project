# reports/forms.py

from django import forms
from workers.models import Trabajador
from core.models import UnidadAdministrativa


class ReporteTrabajadorForm(forms.Form):
    trabajador = forms.ModelChoiceField(
        queryset=Trabajador.objects.none(),
        label="Trabajador"
    )
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        qs = Trabajador.objects.filter(activo=True)

        if user is not None:
            perfil = user.perfilusuario
            if perfil.rol == "JEFE":
                # Solo trabajadores de la unidad del jefe
                qs = qs.filter(unidad=perfil.trabajador.unidad)

        self.fields["trabajador"].queryset = qs

class ReporteUnidadForm(forms.Form):
    unidad = forms.ModelChoiceField(
        queryset=UnidadAdministrativa.objects.none(),
        label="Unidad Administrativa"
    )
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        qs = UnidadAdministrativa.objects.all()

        if user is not None:
            perfil = user.perfilusuario
            if perfil.rol == "JEFE":
                qs = UnidadAdministrativa.objects.filter(
                    pk=perfil.trabajador.unidad_id
                )
                # Opcional: para que salga seleccionada desde el inicio
                self.fields["unidad"].initial = perfil.trabajador.unidad

        self.fields["unidad"].queryset = qs
