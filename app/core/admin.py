from django.contrib import admin
from .models import (
    Puesto, TipoNombramiento,
    TipoIncidencia, UnidadAdministrativa,
    CalendarioLaboral
)

@admin.register(UnidadAdministrativa)
class UnidadAdministrativaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad_padre', 'created_at', 'updated_at', 'created_by', 'updated_by')
    search_fields = ('nombre',)

@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre_puesto', 'nivel', 'created_at', 'updated_at', 'created_by', 'updated_by')
    search_fields = ('nombre_puesto',)

@admin.register(TipoNombramiento)
class TipoNombramientoAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'created_at', 'updated_at', 'created_by', 'updated_by')

@admin.register(TipoIncidencia)
class TipoIncidenciaAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'created_at', 'updated_at', 'created_by', 'updated_by')

@admin.register(CalendarioLaboral)
class CalendarioLaboralAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'descripcion', 'es_inhabil', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('es_inhabil',)
    ordering = ('fecha',)
