from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from core.audit_views import AuditViewMixin

from .models import Trabajador, JornadaLaboral, TrabajadorJornada
from .forms import TrabajadorForm, JornadaLaboralForm, AsignarJornadaForm

from accounts.mixins import (
    SoloAdminMixin,
    SoloJefeMixin,
    SoloTrabajadorMixin,
    AdminOJefeMixin,
    OwnerOrAdminOJefeMixin
)

from django.db.models import Prefetch, Q
from django.db import transaction
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone


# ============================================
# LISTA DE TRABAJADORES
# Solo ADMIN o JEFE (pero JEFE sólo trabajadores de su unidad)
# ============================================

class TrabajadorListView(LoginRequiredMixin, AdminOJefeMixin, ListView):
    model = Trabajador
    template_name = 'workers/lista_trabajadores.html'
    context_object_name = 'trabajadores'
    paginate_by = 10

    def get_queryset(self):
        hoy = timezone.now().date()

        qs = (
            Trabajador.objects
            .select_related('unidad', 'puesto', 'tipo_nombramiento')
            .prefetch_related(
                Prefetch(
                    'jornadas',
                    queryset=TrabajadorJornada.objects.filter(
                        Q(fecha_fin__isnull=True) | Q(fecha_fin__gt=hoy)
                    ).select_related('jornada'),
                    to_attr='jornada_activa'
                )
            )
            .filter(activo=True)  # Solo activos
            .order_by('apellido_paterno')
        )

        # Si es JEFE, restringimos trabajadores a su unidad
        perfil = self.request.user.perfilusuario
        if perfil.rol == 'JEFE':
            qs = qs.filter(unidad=perfil.trabajador.unidad)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        trabajadores = context['trabajadores']

        # Estadísticas
        context['total_trabajadores'] = trabajadores.count()
        context['total_activos'] = trabajadores.count()  # Como el queryset ya filtra activos

        return context


# =============================
# CRUD DE TRABAJADORES
# =============================

class TrabajadorCreateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, CreateView):
    model = Trabajador
    form_class = TrabajadorForm
    template_name = 'workers/trabajador_form.html'
    success_url = reverse_lazy('workers:trabajador_list')


class TrabajadorUpdateView(LoginRequiredMixin, AdminOJefeMixin, AuditViewMixin, UpdateView):
    model = Trabajador
    form_class = TrabajadorForm
    template_name = 'workers/trabajador_form.html'
    success_url = reverse_lazy('workers:trabajador_list')

    def get_queryset(self):
        qs = super().get_queryset()
        perfil = self.request.user.perfilusuario

        if perfil.rol == 'JEFE':
            return qs.filter(unidad=perfil.trabajador.unidad)

        return qs


class TrabajadorDetailView(LoginRequiredMixin, OwnerOrAdminOJefeMixin, DetailView):
    model = Trabajador
    template_name = 'workers/trabajador_detail.html'
    context_object_name = 'trabajador'


class TrabajadorDeleteView(LoginRequiredMixin, SoloAdminMixin, DeleteView):
    model = Trabajador
    template_name = 'workers/trabajador_confirm_delete.html'
    success_url = reverse_lazy('workers:trabajador_list')


# =============================
# CRUD DE JORNADAS LABORALES
# Solo ADMIN
# =============================

class JornadaListView(LoginRequiredMixin, SoloAdminMixin, ListView):
    model = JornadaLaboral
    template_name = 'workers/lista_jornadas.html'
    context_object_name = 'jornadas'

    def get_queryset(self):
        hoy = timezone.now().date()

        return (
            JornadaLaboral.objects
            .prefetch_related(
                Prefetch(
                    'trabajadorjornada_set',
                    queryset=TrabajadorJornada.objects.filter(
                        fecha_fin__isnull=True
                    ).select_related('trabajador'),
                    to_attr='trabajadores_activos'
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        jornadas = context['jornadas']

        # Contar trabajadores asignados
        total_asignados = sum(len(j.trabajadores_activos) for j in jornadas)

        # Contar trabajadores totales activos
        total_trabajadores = Trabajador.objects.filter(activo=True).count()

        # Sin asignar = trabajadores activos - los que tienen jornada
        sin_asignar = total_trabajadores - total_asignados

        context['total_asignados'] = total_asignados
        context['sin_asignar'] = sin_asignar

        return context


class JornadaCreateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, CreateView):
    model = JornadaLaboral
    form_class = JornadaLaboralForm
    template_name = 'workers/jornada_form.html'
    success_url = reverse_lazy('workers:jornada_list')


class JornadaUpdateView(LoginRequiredMixin, SoloAdminMixin, AuditViewMixin, UpdateView):
    model = JornadaLaboral
    form_class = JornadaLaboralForm
    template_name = 'workers/jornada_form.html'
    success_url = reverse_lazy('workers:jornada_list')


class JornadaDeleteView(LoginRequiredMixin, SoloAdminMixin, DeleteView):
    model = JornadaLaboral
    template_name = 'workers/jornada_confirm_delete.html'
    success_url = reverse_lazy('workers:jornada_list')

# =============================
# ASIGNACIÓN DE JORNADAS
# ADMIN o JEFE (pero JEFE solo en su unidad)
# =============================

class AsignarJornadaCreateView(LoginRequiredMixin, AdminOJefeMixin, AuditViewMixin, CreateView):
    model = TrabajadorJornada
    form_class = AsignarJornadaForm
    template_name = 'workers/asignar_jornada.html'
    success_url = reverse_lazy('workers:jornada_list')

    
    def get_initial(self):
        initial = super().get_initial()

        # Obtener parámetros de la URL
        trabajador_id = self.request.GET.get("trabajador")
        jornada_id = self.request.GET.get("jornada")

        # Preseleccionar trabajador si viene en la URL
        if trabajador_id:
            initial["trabajador"] = trabajador_id

        # Preseleccionar jornada si también viene en la URL
        if jornada_id:
            initial["jornada"] = jornada_id

        return initial

    def form_valid(self, form):
        nueva = form.save(commit=False)
        trabajador = nueva.trabajador

        # Si es jefe, solo puede asignar a su unidad
        perfil = self.request.user.perfilusuario
        if perfil.rol == 'JEFE' and trabajador.unidad != perfil.trabajador.unidad:
            form.add_error(None, "No tiene permiso para asignar jornada a trabajadores de otra unidad.")
            return self.form_invalid(form)

        fecha_inicio = nueva.fecha_inicio

        with transaction.atomic():
            turno_anterior = TrabajadorJornada.objects.filter(
                trabajador=trabajador,
                fecha_fin__isnull=True
            ).first()

            if turno_anterior:
                if fecha_inicio <= turno_anterior.fecha_inicio:
                    form.add_error('fecha_inicio', "La nueva jornada debe iniciar después de la actual.")
                    return self.form_invalid(form)

                turno_anterior.fecha_fin = fecha_inicio - timedelta(days=1)
                turno_anterior.save()

        messages.success(self.request, f"Jornada asignada correctamente a {trabajador}")

        return super().form_valid(form)
