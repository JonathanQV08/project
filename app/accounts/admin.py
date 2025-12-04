from django.contrib import admin
from .models import PerfilUsuario

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """
    Configuración personalizada del modelo PerfilUsuario en el admin.
    Permite búsqueda por usuario y filtrado por rol.
    """
    list_display = ('user', 'rol', 'trabajador')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__email')
