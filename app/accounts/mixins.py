# accounts/mixins.py
# Mixins de control de acceso para vistas basadas en roles

from django.contrib.auth.mixins import UserPassesTestMixin
from .utils import es_admin, es_jefe, es_trabajador, get_perfil

from django.shortcuts import redirect

# ============================================================
# BASE
# ============================================================

class BaseRolMixin(UserPassesTestMixin):
    """
    Base para todos los mixins de roles.
    Centraliza el acceso al perfil del usuario.
    """
    def get_perfil(self):
        return get_perfil(self.request.user)


# ============================================================
# MIXINS INDIVIDUALES POR ROL
# ============================================================

class SoloAdminMixin(BaseRolMixin):
    """Acceso exclusivo para Administradores."""
    def test_func(self):
        return es_admin(self.request.user)


class SoloJefeMixin(BaseRolMixin):
    """Acceso exclusivo para Jefes."""
    def test_func(self):
        return es_jefe(self.request.user)


class SoloTrabajadorMixin(BaseRolMixin):
    """Acceso exclusivo para Trabajadores."""
    def test_func(self):
        return es_trabajador(self.request.user)


# ============================================================
# MIXINS COMBINADOS
# ============================================================

class AdminOJefeMixin(BaseRolMixin):
    """Acceso para Administradores o Jefes."""
    def test_func(self):
        user = self.request.user
        return es_admin(user) or es_jefe(user)

class TrabajadorOJefeMixin(BaseRolMixin):
    """Acceso para Trabajadores o Jefes."""
    def test_func(self):
        user = self.request.user
        return es_trabajador(user) or es_jefe(user)
    
class SoloJefeDeLaUnidadMixin(BaseRolMixin):
    """
    JEFE puede acceder solo si el objeto corresponde a su unidad organizacional.
    Requiere que el objeto tenga atributo: id_unidad
    """
    def test_func(self):
        user = self.request.user
        perfil = self.get_perfil()

        if not es_jefe(user):
            return False

        objeto = self.get_object()
        return objeto.id_unidad == perfil.trabajador.id_unidad


# ============================================================
# MIXIN ORIGINAL (basado en `.user`)
# ============================================================

class OwnerOrAdminOJefeMixin(BaseRolMixin):
    """
    Este mixin solo funciona para modelos que tienen campo `user`.
    - El usuario dueño puede acceder
    - Admin o Jefe pueden acceder
    """

    def test_func(self):
        user = self.request.user
        perfil = self.get_perfil()
        obj = self.get_object()

        # Usuario dueño (solo modelos con 'user')
        if hasattr(obj, "user") and obj.user == user:
            return True

        # Admin o Jefe
        return es_admin(user) or es_jefe(user)


# ============================================================
# NUEVO MIXIN ESPECIAL PARA ASISTENCIA
# (RegistroAsistencia no tiene campo `user`, sino `trabajador`)
# ============================================================

class AsistenciaOwnerOrAdminOJefeMixin(BaseRolMixin):
    """
    Permisos para RegistroAsistencia:
    - ADMIN → acceso total
    - JEFE → solo asistencias de su unidad
    - TRABAJADOR → solo su propia asistencia
    """

    def test_func(self):
        user = self.request.user
        perfil = self.get_perfil()
        asistencia = self.get_object()  # RegistroAsistencia

        # ADMIN tiene acceso total
        if es_admin(user):
            return True

        # TRABAJADOR solo puede ver sus propios registros
        if es_trabajador(user) and asistencia.trabajador == perfil.trabajador:
            return True

        # JEFE puede acceder si el trabajador pertenece a su unidad
        if es_jefe(user):
            if asistencia.trabajador.unidad == perfil.trabajador.unidad:
                return True

        return False

# ============================================================
# NUEVO MIXIN ESPECIAL PARA INCIDENCIAS
# (Incidencia no tiene campo `user`, sino `trabajador`)
# ============================================================

class IncidenciaOwnerOrAdminOJefeMixin(BaseRolMixin):
    """
    Permisos para incidencias:
    - ADMIN → todas
    - JEFE → incidencias de trabajadores de su unidad
    - TRABAJADOR → solo sus propias incidencias
    """

    def test_func(self):
        user = self.request.user
        perfil = self.get_perfil()
        incidencia = self.get_object()

        if es_admin(user):
            return True

        if es_trabajador(user) and incidencia.trabajador == perfil.trabajador:
            return True

        if es_jefe(user):
            if incidencia.trabajador.unidad == perfil.trabajador.unidad:
                return True

        return False
    
# ============================================================
# MIXINS DE REDIRECCIÓN PARA TRABAJADORES
# ============================================================

class RedirigirTrabajadorAsistenciaMixin:
    """
    Si un trabajador intenta acceder a la vista de ADMIN/JEFE,
    lo redirigimos automáticamente a 'mis_asistencias'.
    """

    def dispatch(self, request, *args, **kwargs):
        perfil = get_perfil(request.user)

        if es_trabajador(request.user):
            return redirect('attendance:mis_asistencias')

        return super().dispatch(request, *args, **kwargs)
    
    
class RedirigirTrabajadorIncidenciasMixin:
    """
    Si un trabajador intenta acceder a la vista de ADMIN/JEFE de incidencias,
    lo redirigimos automáticamente a 'mis_incidencias'.
    """

    def dispatch(self, request, *args, **kwargs):
        perfil = get_perfil(request.user)

        if es_trabajador(request.user):
            return redirect('incidents:mis_incidencias')

        return super().dispatch(request, *args, **kwargs)