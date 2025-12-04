# incidents/views.py
# Vistas para incidencias de trabajadores

from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.mixins import (
    SoloTrabajadorMixin,
    AdminOJefeMixin,
    IncidenciaOwnerOrAdminOJefeMixin,
    RedirigirTrabajadorIncidenciasMixin,   # <-- IMPORTANTE
)
from accounts.utils import get_perfil, es_jefe
from core.audit_views import AuditViewMixin
from .models import Incidencia
from .forms import IncidenciaTrabajadorForm, IncidenciaAdminForm


# ============================================================
# LISTA GENERAL (ADMIN / JEFE)
# ============================================================

class IncidenciaListView(
    LoginRequiredMixin,
    RedirigirTrabajadorIncidenciasMixin,
    AdminOJefeMixin,
    ListView
):
    model = Incidencia
    template_name = 'incidents/incidencia_list.html'
    context_object_name = 'incidencias'
    paginate_by = 20

    def get_queryset(self):
        qs = (
            Incidencia.objects
            .select_related('trabajador', 'tipo')
            .order_by('-fecha_inicio', 'trabajador__apellido_paterno')
        )

        perfil = get_perfil(self.request.user)

        # JEFE: solo incidencias de su unidad
        if es_jefe(self.request.user):
            qs = qs.filter(trabajador__unidad=perfil.trabajador.unidad)

        # Guardamos queryset base para estadísticas
        self.qs_base = qs

        # Filtro adicional por estatus (solo para la tabla)
        estatus = self.request.GET.get('estatus')
        if estatus:
            qs = qs.filter(estatus=estatus)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        base_qs = getattr(self, 'qs_base', Incidencia.objects.none())

        # Estadísticas por estatus según modelo
        context['total_pendientes'] = base_qs.filter(estatus='PENDIENTE').count()
        context['total_aprobadas'] = base_qs.filter(estatus='APROBADA').count()
        context['total_rechazadas'] = base_qs.filter(estatus='RECHAZADA').count()

        # Para resaltar filtros en UI (opcional)
        context['estatus_seleccionado'] = self.request.GET.get('estatus')

        return context


# ============================================================
# CREAR / EDITAR (ADMIN / JEFE)
# ============================================================

class IncidenciaCreateView(LoginRequiredMixin, AdminOJefeMixin, AuditViewMixin, CreateView):
    model = Incidencia
    form_class = IncidenciaAdminForm
    template_name = 'incidents/incidencia_form.html'
    success_url = reverse_lazy('incidents:incidencia_list')

    def form_valid(self, form):
        incidencia = form.save(commit=False)
        if incidencia.estatus == 'APROBADA' and incidencia.aprobada_por is None:
            incidencia.aprobada_por = self.request.user        
        return super().form_valid(form)


class IncidenciaUpdateView(LoginRequiredMixin, AdminOJefeMixin, AuditViewMixin, UpdateView):
    model = Incidencia
    form_class = IncidenciaAdminForm
    template_name = 'incidents/incidencia_form.html'
    success_url = reverse_lazy('incidents:incidencia_list')

    def form_valid(self, form):
        incidencia = form.save(commit=False)
        # Si la están aprobando en este momento, registra quién la aprueba
        if incidencia.estatus == 'APROBADA' and incidencia.aprobada_por is None:
            incidencia.aprobada_por = self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        qs = super().get_queryset()
        perfil = get_perfil(self.request.user)

        if es_jefe(self.request.user):
            return qs.filter(trabajador__unidad=perfil.trabajador.unidad)

        return qs


# ============================================================
# DETALLE (Admin/Jefe o dueño)
# ============================================================

class IncidenciaDetailView(LoginRequiredMixin, IncidenciaOwnerOrAdminOJefeMixin, DetailView):
    model = Incidencia
    template_name = 'incidents/incidencia_detail.html'
    context_object_name = 'incidencia'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incidencia = context['incidencia']

        # Calcular días de duración (inclusivo)
        dias = (incidencia.fecha_fin - incidencia.fecha_inicio).days + 1

        context['duracion_dias'] = dias
        return context



# ============================================================
# FLUJO DEL TRABAJADOR
# ============================================================

class MisIncidenciasListView(LoginRequiredMixin, SoloTrabajadorMixin, ListView):
    model = Incidencia
    template_name = 'incidents/mis_incidencias.html'
    context_object_name = 'incidencias'
    paginate_by = 20

    def get_queryset(self):
        perfil = get_perfil(self.request.user)

        qs = (
            Incidencia.objects
            .filter(trabajador=perfil.trabajador)
            .select_related('tipo')
            .order_by('-fecha_inicio')
        )

        # Guardamos el queryset completo para estadísticas
        self.qs_base = qs

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        base = getattr(self, 'qs_base', Incidencia.objects.none())

        context['total_pendientes'] = base.filter(estatus='PENDIENTE').count()
        context['total_aprobadas'] = base.filter(estatus='APROBADA').count()
        context['total_rechazadas'] = base.filter(estatus='RECHAZADA').count()

        return context


class NuevaIncidenciaTrabajadorView(LoginRequiredMixin, SoloTrabajadorMixin, AuditViewMixin, CreateView):
    model = Incidencia
    form_class = IncidenciaTrabajadorForm
    template_name = 'incidents/incidencia_trabajador_form.html'
    success_url = reverse_lazy('incidents:mis_incidencias')

    def form_valid(self, form):
        perfil = get_perfil(self.request.user)

        incidencia = form.save(commit=False)
        incidencia.trabajador = perfil.trabajador
        incidencia.estatus = 'PENDIENTE'

        return super().form_valid(form)   
