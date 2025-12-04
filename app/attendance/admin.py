from django.contrib import admin
from .models import RegistroAsistencia

@admin.register(RegistroAsistencia)
class RegistroAsistenciaAdmin(admin.ModelAdmin):
    list_display = (
        'trabajador',
        'fecha',
        'hora_entrada',
        'hora_salida',
        'estatus',
        'minutos_retardo',
        'horas_trabajadas',
        'incidencia',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )

    list_filter = (
        'estatus',
        'fecha',
        'trabajador__unidad',
        'incidencia'
    )

    search_fields = (
        'trabajador__nombre',
        'trabajador__apellido_paterno',
        'trabajador__numero_empleado'
    )

    ordering = ('-fecha',)
    list_per_page = 20
