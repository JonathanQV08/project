from .models import PerfilUsuario

def get_perfil(user):
    """Retorna el perfil del usuario o None si no existe."""
    return getattr(user, 'perfilusuario', None)

def es_admin(user):
    perfil = get_perfil(user)
    return perfil and perfil.rol == 'ADMIN'

def es_jefe(user):
    perfil = get_perfil(user)
    return perfil and perfil.rol == 'JEFE'

def es_trabajador(user):
    perfil = get_perfil(user)
    return perfil and perfil.rol == 'TRAB'
