from django.contrib import admin
from .models import Incidencia

@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = (
        'trabajador',
        'tipo',
        'fecha_inicio',
        'fecha_fin',
        'estatus',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'aprobada_por',
    )

    list_filter = ('estatus', 'tipo', 'fecha_inicio', 'trabajador__unidad')

    search_fields = (
        'trabajador__nombre',
        'trabajador__apellido_paterno',
        'trabajador__numero_empleado',
        'motivo',
    )

    ordering = ('-fecha_inicio',)
