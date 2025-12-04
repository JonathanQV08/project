from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin

# Formularios
from core.audit_views import AuditViewMixin
from core.forms import (
    CalendarioLaboralForm, PuestoForm, TipoIncidenciaForm,
    TipoNombramientoForm, UnidadAdministrativaForm
)

# Modelos
from .models import (
    CalendarioLaboral, Puesto, TipoNombramiento,
    TipoIncidencia, UnidadAdministrativa
)

# Importación de roles centralizados
from accounts.mixins import SoloAdminMixin, AdminOJefeMixin

# ========================================
# UNIDADES ADMINISTRATIVAS - Solo ADMIN
# ========================================

class UnidadListView(LoginRequiredMixin, SoloAdminMixin, ListView):
    model = UnidadAdministrativa
    template_name = 'core/unidad_list.html'
    context_object_name = 'unidades'
    paginate_by = 10


class UnidadCreateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, CreateView):
    model = UnidadAdministrativa
    form_class = UnidadAdministrativaForm
    template_name = 'core/unidad_form.html'
    success_url = reverse_lazy('core:unidad_list')


class UnidadUpdateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, UpdateView):
    model = UnidadAdministrativa
    form_class = UnidadAdministrativaForm
    template_name = 'core/unidad_form.html'
    success_url = reverse_lazy('core:unidad_list')


class UnidadDeleteView(LoginRequiredMixin, SoloAdminMixin, DeleteView):
    model = UnidadAdministrativa
    template_name = 'core/unidad_confirm_delete.html'
    success_url = reverse_lazy('core:unidad_list')

# ============================
# PUESTOS  – Solo ADMIN
# ============================

class PuestoListView(LoginRequiredMixin, SoloAdminMixin, ListView):
    model = Puesto
    template_name = 'core/puesto_list.html'
    context_object_name = 'puestos'
    paginate_by = 10


class PuestoCreateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, CreateView):
    model = Puesto
    form_class = PuestoForm
    template_name = 'core/puesto_form.html'
    success_url = reverse_lazy('core:puesto_list')


class PuestoUpdateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, UpdateView):
    model = Puesto
    form_class = PuestoForm
    template_name = 'core/puesto_form.html'
    success_url = reverse_lazy('core:puesto_list')


class PuestoDeleteView(LoginRequiredMixin, SoloAdminMixin, DeleteView):
    model = Puesto
    template_name = 'core/puesto_confirm_delete.html'
    success_url = reverse_lazy('core:puesto_list')    

# =========================================
# TIPOS DE NOMBRAMIENTO – Solo ADMIN
# =========================================

class TipoNombramientoListView(LoginRequiredMixin, SoloAdminMixin, ListView):
    model = TipoNombramiento
    template_name = 'core/nombramiento_list.html'
    context_object_name = 'nombramientos'
    paginate_by = 10


class TipoNombramientoCreateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, CreateView):
    model = TipoNombramiento
    form_class = TipoNombramientoForm
    template_name = 'core/nombramiento_form.html'
    success_url = reverse_lazy('core:nombramiento_list')


class TipoNombramientoUpdateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, UpdateView):
    model = TipoNombramiento
    form_class = TipoNombramientoForm
    template_name = 'core/nombramiento_form.html'
    success_url = reverse_lazy('core:nombramiento_list')


class TipoNombramientoDeleteView(LoginRequiredMixin, SoloAdminMixin, DeleteView):
    model = TipoNombramiento
    template_name = 'core/nombramiento_confirm_delete.html'
    success_url = reverse_lazy('core:nombramiento_list')

# =====================================
# TIPOS DE INCIDENCIA – Solo ADMIN
# =====================================

class TipoIncidenciaListView(LoginRequiredMixin, SoloAdminMixin, ListView):
    model = TipoIncidencia
    template_name = 'core/incidencia_tipo_list.html'
    context_object_name = 'tipos_incidencia'
    paginate_by = 10


class TipoIncidenciaCreateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, CreateView):
    model = TipoIncidencia
    form_class = TipoIncidenciaForm
    template_name = 'core/incidencia_tipo_form.html'
    success_url = reverse_lazy('core:tipo_incidencia_list')


class TipoIncidenciaUpdateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, UpdateView):
    model = TipoIncidencia
    form_class = TipoIncidenciaForm
    template_name = 'core/incidencia_tipo_form.html'
    success_url = reverse_lazy('core:tipo_incidencia_list')


class TipoIncidenciaDeleteView(LoginRequiredMixin, SoloAdminMixin, DeleteView):
    model = TipoIncidencia
    template_name = 'core/incidencia_tipo_confirm_delete.html'
    success_url = reverse_lazy('core:tipo_incidencia_list')

# ================================
# CALENDARIO LABORAL 
# Accesible para ADMIN y JEFE
# ================================

class CalendarioListView(LoginRequiredMixin, AdminOJefeMixin, ListView):
    model = CalendarioLaboral
    template_name = 'core/calendario_list.html'
    context_object_name = 'eventos'
    ordering = ['fecha']


class CalendarioCreateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, CreateView):
    """
    Crear días inhábiles: reservado a ADMIN.
    JEFE solo puede consultarlos porque impactan asistencias.
    """
    model = CalendarioLaboral
    form_class = CalendarioLaboralForm
    template_name = 'core/calendario_form.html'
    success_url = reverse_lazy('core:calendario_list')


class CalendarioUpdateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, UpdateView):
    model = CalendarioLaboral
    form_class = CalendarioLaboralForm
    template_name = 'core/calendario_form.html'
    success_url = reverse_lazy('core:calendario_list')


class CalendarioDeleteView(LoginRequiredMixin, SoloAdminMixin, DeleteView):
    model = CalendarioLaboral
    template_name = 'core/calendario_confirm_delete.html'
    success_url = reverse_lazy('core:calendario_list')    

# ===============================
# DASHBOARD PRINCIPAL DEL MÓDULO
# ===============================

class CoreDashboardView(LoginRequiredMixin, SoloAdminMixin, TemplateView):
    """
    Dashboard general del módulo CORE (catálogos).
    Acceso exclusivo para Administradores.
    """
    template_name = 'core/dashboard.html'    