# attendance/views.py
# Vistas del módulo de asistencia
# Basadas en el estilo de workers/views.py (roles, mixins, estructura limpia)

from pyexpat.errors import messages
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from core.models import CalendarioLaboral
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import (
    AsistenciaOwnerOrAdminOJefeMixin,
    AdminOJefeMixin,
    RedirigirTrabajadorAsistenciaMixin,
    SoloTrabajadorMixin,
)
from core.audit_views import AuditViewMixin
from .models import RegistroAsistencia
from .forms import AsistenciaAdminForm, AsistenciaTrabajadorForm


# ============================================================
# LISTA GENERAL (ADMIN / JEFE)
# ============================================================

class AsistenciaListView(LoginRequiredMixin, RedirigirTrabajadorAsistenciaMixin, AdminOJefeMixin, ListView):
    model = RegistroAsistencia
    template_name = 'attendance/lista_asistencias.html'
    context_object_name = 'asistencias'
    paginate_by = 20

    def get_queryset(self):
        qs = (
            RegistroAsistencia.objects
            .select_related('trabajador', 'incidencia')
            .order_by('-fecha', 'trabajador__apellido_paterno')
        )

        perfil = self.request.user.perfilusuario

        # JEFE: solo trabajadores de su unidad
        if perfil.rol == 'JEFE':
            qs = qs.filter(trabajador__unidad=perfil.trabajador.unidad)

        self._qs_for_stats = qs   # <- Guardamos el queryset para stats

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = getattr(self, '_qs_for_stats', RegistroAsistencia.objects.none())

        context["total_puntuales"] = qs.filter(estatus="NORMAL").count()
        context["total_retardos"] = qs.filter(estatus="RETARDO").count()
        context["total_faltas"] = qs.filter(estatus="FALTA").count()
        context["total_justificadas"] = qs.filter(estatus="JUSTIFICADA").count()

        return context



# ============================================================
# CREAR ASISTENCIA (ADMIN / JEFE)
# ============================================================

class AsistenciaCreateView(LoginRequiredMixin, AdminOJefeMixin, AuditViewMixin, CreateView):
    model = RegistroAsistencia
    form_class = AsistenciaAdminForm
    template_name = 'attendance/asistencia_form.html'
    success_url = reverse_lazy('attendance:asistencia_list')

# ============================================================
# EDITAR ASISTENCIA (ADMIN / JEFE)
# JEFE solo puede editar registros de su unidad
# ============================================================

class AsistenciaUpdateView(LoginRequiredMixin, AdminOJefeMixin, AuditViewMixin, UpdateView):
    model = RegistroAsistencia
    form_class = AsistenciaAdminForm
    template_name = 'attendance/asistencia_form.html'
    success_url = reverse_lazy('attendance:asistencia_list')

    def get_queryset(self):
        qs = super().get_queryset().select_related("trabajador")

        perfil = self.request.user.perfilusuario

        # JEFE solo puede editar registros de su unidad
        if perfil.rol == 'JEFE':
            return qs.filter(trabajador__unidad=perfil.trabajador.unidad)

        return qs


# ============================================================
# DETALLE DE ASISTENCIA
# Acceso: Admin / Jefe o el propio trabajador
# ============================================================

class AsistenciaDetailView(LoginRequiredMixin, AsistenciaOwnerOrAdminOJefeMixin, DetailView):
    model = RegistroAsistencia
    template_name = 'attendance/asistencia_detail.html'
    context_object_name = 'asistencia'
    

# ============================================================
# REGISTRO PERSONAL (TRABAJADOR)
# No elige trabajador ni fecha → se asignan automáticamente
# ============================================================

class MiAsistenciaCreateView(LoginRequiredMixin, SoloTrabajadorMixin, AuditViewMixin, CreateView):
    model = RegistroAsistencia
    form_class = AsistenciaTrabajadorForm
    template_name = 'attendance/marcar_asistencia.html'
    success_url = reverse_lazy('attendance:mis_asistencias')

    def dispatch(self, request, *args, **kwargs):
        hoy = timezone.now().date()

        dia_inhabil = CalendarioLaboral.objects.filter(
            fecha=hoy,
            es_inhabil=True
        ).first()

        if dia_inhabil:
            # Mostrar alerta visual en la pantalla de Mis Asistencias
            messages.error(
                request,
                f"Hoy es un día inhábil: {dia_inhabil.descripcion}. "
                "No puedes registrar asistencia."
            )
            return redirect("attendance:mis_asistencias")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        trabajador = self.request.user.perfilusuario.trabajador
        hoy = timezone.now().date()

        # Verificar si ya existe un registro hoy
        existente = RegistroAsistencia.objects.filter(
            trabajador=trabajador,
            fecha=hoy
        ).first()

        if existente:
            messages.warning(
                self.request,
                "Ya registraste asistencia hoy. No es posible duplicar el registro."
            )
            return redirect('attendance:mis_asistencias')

        # Crear nuevo registro
        asistencia = form.save(commit=False)
        asistencia.trabajador = trabajador
        asistencia.fecha = hoy
        asistencia.save()

        messages.success(self.request, "Asistencia registrada correctamente.")
        return redirect(self.success_url)



# ============================================================
# LISTA PERSONAL DEL TRABAJADOR
# ============================================================

class MisAsistenciasListView(LoginRequiredMixin, SoloTrabajadorMixin, ListView):
    model = RegistroAsistencia
    template_name = 'attendance/mis_asistencias.html'
    context_object_name = 'asistencias'
    paginate_by = 20

    def get_queryset(self):
        trabajador = self.request.user.perfilusuario.trabajador

        qs = (
            RegistroAsistencia.objects
            .filter(trabajador=trabajador)
            .order_by('-fecha')
        )

        # Guardamos el queryset para estadísticas
        self._qs_for_stats = qs
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = getattr(self, "_qs_for_stats", RegistroAsistencia.objects.none())

        context["total_puntuales"]     = qs.filter(estatus="NORMAL").count()
        context["total_retardos"]      = qs.filter(estatus="RETARDO").count()
        context["total_faltas"]        = qs.filter(estatus="FALTA").count()
        context["total_justificadas"]  = qs.filter(estatus="JUSTIFICADA").count()

        # Si algún día quieres mostrar esto:
        context["total_inhabiles"]     = qs.filter(estatus="INHABIL").count()

        return context
