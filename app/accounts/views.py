from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q

from .models import PerfilUsuario
from .forms import PerfilUsuarioForm

from .mixins import (
    SoloAdminMixin,
    OwnerOrAdminOJefeMixin
)


class PerfilUsuarioListView(LoginRequiredMixin, SoloAdminMixin, ListView):
    """
    Lista de perfiles — solo Administradores.
    Incluye búsqueda, filtros y métricas.
    """
    model = PerfilUsuario
    template_name = 'accounts/perfil_list.html'
    context_object_name = 'perfiles'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')

        # Búsqueda por texto
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(user__username__icontains=q) |
                Q(user__email__icontains=q) |
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q)
            )

        # Filtro por rol
        rol = self.request.GET.get('rol', '').lower()
        mapa_roles = {
            'admin': 'ADMIN',
            'jefe': 'JEFE',
            'usuario': 'TRAB'
        }
        rol_modelo = mapa_roles.get(rol)
        if rol_modelo:
            queryset = queryset.filter(rol=rol_modelo)

        return queryset.order_by('user__username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_usuarios'] = PerfilUsuario.objects.count()
        context['total_admins'] = PerfilUsuario.objects.filter(rol='ADMIN').count()
        context['total_jefes'] = PerfilUsuario.objects.filter(rol='JEFE').count()
        context['total_usuarios_reg'] = PerfilUsuario.objects.filter(rol='TRAB').count()
        context['total_vinculados'] = PerfilUsuario.objects.filter(
            trabajador__isnull=False).count()
        return context


class PerfilUsuarioCreateView(LoginRequiredMixin, SoloAdminMixin, CreateView):
    """
    Crear un nuevo perfil — Solo Administradores.
    """
    model = PerfilUsuario
    form_class = PerfilUsuarioForm
    template_name = 'accounts/perfil_form.html'
    success_url = reverse_lazy('perfil_list')


class PerfilUsuarioUpdateView(LoginRequiredMixin, SoloAdminMixin, UpdateView):
    """
    Editar un perfil — Solo Administradores.
    """
    model = PerfilUsuario
    form_class = PerfilUsuarioForm
    template_name = 'accounts/perfil_form.html'
    success_url = reverse_lazy('perfil_list')


class MiPerfilView(LoginRequiredMixin, OwnerOrAdminOJefeMixin, DetailView):
    """
    Ver perfil propio, o visto por Admin/Jefe según reglas.
    – Trabajador: ve su propio perfil.
    – Jefe/Admin: pueden consultar cualquier perfil (útil para auditoría).
    """
    model = PerfilUsuario
    template_name = 'accounts/mi_perfil.html'

    def get_object(self):
        """
        - Si el usuario es Trabajador: retorna su propio perfil.
        - Si Admin/Jefe: puede consultar el perfil indicado por pk.
        """
        if 'pk' in self.kwargs:
            return PerfilUsuario.objects.get(pk=self.kwargs['pk'])

        # caso normal: /accounts/mi-perfil/
        return PerfilUsuario.objects.get(user=self.request.user)
