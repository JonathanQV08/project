# reports/views.py
# Módulo de reportes de asistencia
# Compatible con roles ADMIN / JEFE / TRABAJADOR
# Usa los modelos existentes del sistema SCA-B123

from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, TemplateView
from django.http import HttpResponse
from django.utils.timezone import now
from django.utils.dateparse import parse_date

from accounts.mixins import (
    AdminOJefeMixin,
    SoloTrabajadorMixin,
    TrabajadorOJefeMixin
)

from workers.models import Trabajador
from attendance.models import RegistroAsistencia
from core.models import UnidadAdministrativa
from django.http import HttpResponseForbidden

from .forms import (
    ReporteTrabajadorForm,
    ReporteUnidadForm
)

import csv


# ============================================================
# 1. REPORTE POR TRABAJADOR (ADMIN / JEFE)
# ============================================================

class ReportePorTrabajadorView(AdminOJefeMixin, FormView):
    template_name = "reports/reporte_trabajador_form.html"
    form_class = ReporteTrabajadorForm

    def get_form_kwargs(self):
        """
        Pasamos el user al formulario para que limite el queryset:
        ADMIN -> todos los trabajadores
        JEFE -> solo trabajadores de su unidad
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        trabajador = form.cleaned_data['trabajador']
        fi = form.cleaned_data['fecha_inicio']
        ff = form.cleaned_data['fecha_fin']

        perfil = self.request.user.perfilusuario

        # Doble seguro: si es JEFE, no debe poder ver trabajadores de otra unidad
        if perfil.rol == "JEFE" and trabajador.unidad_id != perfil.trabajador.unidad_id:
            return HttpResponseForbidden("No tiene permiso para ver este trabajador.")

        asistencias = (
            RegistroAsistencia.objects
            .filter(
                trabajador=trabajador,
                fecha__range=(fi, ff)
            )
            .select_related("trabajador", "incidencia")
            .order_by("fecha")
        )

        return self.render_to_response({
            "form": form,
            "trabajador": trabajador,
            "asistencias": asistencias,
            "fi": fi,
            "ff": ff,
        })


# ============================================================
# CSV – Exportación por trabajador
# ============================================================

@login_required
def exportar_csv_trabajador(request):
    trabajador_id = request.GET.get("t")
    fi_str = request.GET.get("fi")
    ff_str = request.GET.get("ff")

    if not (trabajador_id and fi_str and ff_str):
        return HttpResponse("Parámetros incompletos", status=400)

    fi = parse_date(fi_str)
    ff = parse_date(ff_str)

    if not fi or not ff:
        return HttpResponse("Formato de fecha inválido. Use YYYY-MM-DD.", status=400)

    try:
        trabajador = Trabajador.objects.get(pk=trabajador_id)
    except Trabajador.DoesNotExist:
        return HttpResponse("Trabajador no encontrado", status=404)

    perfil = request.user.perfilusuario

    # JEFE solo puede exportar de trabajadores de su unidad
    if perfil.rol == "JEFE" and trabajador.unidad_id != perfil.trabajador.unidad_id:
        return HttpResponseForbidden("No tiene permiso para ver este trabajador.")

    asistencias = RegistroAsistencia.objects.filter(
        trabajador=trabajador,
        fecha__range=(fi, ff)
    ).order_by("fecha")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename=\"reporte_{trabajador}_{fi.isoformat()}_a_{ff.isoformat()}.csv\"'
    )

    writer = csv.writer(response)
    writer.writerow([
        "Fecha", "Entrada", "Salida",
        "Estatus", "Minutos Retardo", "Horas Trabajadas",
        "Tipo Incidencia"
    ])

    for a in asistencias:
        writer.writerow([
            a.fecha,
            a.hora_entrada,
            a.hora_salida,
            a.estatus,
            a.minutos_retardo,
            a.horas_trabajadas,
            a.incidencia.descripcion if a.incidencia else ""
        ])

    return response

# ============================================================
# 2. REPORTE POR UNIDAD (ADMIN / JEFE)
# ============================================================

from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import AdminOJefeMixin
from .forms import ReporteUnidadForm
from attendance.models import RegistroAsistencia
from core.models import UnidadAdministrativa

class ReportePorUnidadView(LoginRequiredMixin, AdminOJefeMixin, FormView):
    template_name = "reports/reporte_unidad_form.html"
    form_class = ReporteUnidadForm

    def get_form_kwargs(self):
        """
        Pasamos el user al form para que allí se limite el queryset
        de unidades (ADMIN ve todas, JEFE solo la suya).
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        unidad = form.cleaned_data['unidad']
        fi = form.cleaned_data['fecha_inicio']
        ff = form.cleaned_data['fecha_fin']

        perfil = self.request.user.perfilusuario

        # Doble seguro: si es JEFE, siempre forzamos su unidad
        if perfil.rol == "JEFE":
            unidad = perfil.trabajador.unidad

        asistencias = (
            RegistroAsistencia.objects
            .filter(
                trabajador__unidad=unidad,
                fecha__range=(fi, ff)
            )
            .select_related("trabajador", "incidencia")
            .order_by("trabajador__apellido_paterno", "fecha")
        )

        return self.render_to_response({
            "form": form,
            "unidad": unidad,
            "asistencias": asistencias,
            "fi": fi,
            "ff": ff,
        })

# ============================================================
# CSV – Exportación por unidad
# ============================================================

@login_required
def exportar_csv_unidad(request):
    unidad_id = request.GET.get("u")
    fi_str = request.GET.get("fi")
    ff_str = request.GET.get("ff")

    if not (fi_str and ff_str):
        return HttpResponse("Parámetros incompletos", status=400)

    fi = parse_date(fi_str)
    ff = parse_date(ff_str)

    if not fi or not ff:
        return HttpResponse("Formato de fecha inválido. Use YYYY-MM-DD.", status=400)

    perfil = request.user.perfilusuario

    if perfil.rol == "JEFE":
        # Ignoramos lo que venga en ?u= y usamos SIEMPRE su unidad
        unidad = perfil.trabajador.unidad
    else:
        # ADMIN: puede usar la unidad que venga en la URL
        if not unidad_id:
            return HttpResponse("Parámetros incompletos", status=400)
        unidad = UnidadAdministrativa.objects.get(pk=unidad_id)

    asistencias = RegistroAsistencia.objects.filter(
        trabajador__unidad=unidad,
        fecha__range=(fi, ff)
    ).select_related("trabajador", "incidencia")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename=\"reporte_unidad_{unidad}_{fi.isoformat()}_a_{ff.isoformat()}.csv\"'
    )

    writer = csv.writer(response)
    writer.writerow([
        "Trabajador",
        "Fecha", "Entrada", "Salida",
        "Estatus", "Minutos Retardo", "Horas Trabajadas",
        "Tipo Incidencia"
    ])

    for a in asistencias.order_by("trabajador__apellido_paterno", "fecha"):
        writer.writerow([
            str(a.trabajador),
            a.fecha,
            a.hora_entrada,
            a.hora_salida,
            a.estatus,
            a.minutos_retardo,
            a.horas_trabajadas,
            a.incidencia.descripcion if a.incidencia else ""
        ])

    return response

# ============================================================
# 3. REPORTE PERSONAL DEL TRABAJADOR
# ============================================================

class ReportePersonalView(TrabajadorOJefeMixin, TemplateView):
    template_name = "reports/reporte_personal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil = self.request.user.perfilusuario
        trabajador = perfil.trabajador

        # Fechas recibidas por GET
        fi = self.request.GET.get("fi")
        ff = self.request.GET.get("ff")

        qs = RegistroAsistencia.objects.filter(
            trabajador=trabajador
        ).select_related("incidencia")

        if fi and ff:
            qs = qs.filter(fecha__range=(fi, ff))

        context["trabajador"] = trabajador
        context["asistencias"] = qs.order_by("fecha")
        context["fi"] = fi
        context["ff"] = ff
        return context

# ============================================================
# DASHBOARD DE REPORTES
# ============================================================

class ReportesDashboardView(TemplateView):
    template_name = "reports/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        perfil = self.request.user.perfilusuario

        context["es_admin"] = perfil.rol == "ADMIN"
        context["es_jefe"] = perfil.rol == "JEFE"
        context["es_trabajador"] = perfil.rol == "TRAB"

        return context
