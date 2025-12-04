from django.contrib import admin
from .models import Trabajador, JornadaLaboral, TrabajadorJornada

@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = (
        'numero_empleado',
        'nombre',
        'apellido_paterno',
        'unidad',
        'puesto',
        'activo',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )

    list_filter = ('activo', 'unidad', 'puesto', 'tipo_nombramiento')

    search_fields = ('nombre', 'apellido_paterno', 'apellido_materno', 'numero_empleado', 'rfc')

    list_per_page = 20


@admin.register(JornadaLaboral)
class JornadaLaboralAdmin(admin.ModelAdmin):
    list_display = (
        'descripcion',
        'hora_entrada',
        'hora_salida',
        'dias_semana',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )
    search_fields = ('descripcion',)


@admin.register(TrabajadorJornada)
class TrabajadorJornadaAdmin(admin.ModelAdmin):
    list_display = (
        'trabajador',
        'jornada',
        'fecha_inicio',
        'fecha_fin',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )

    list_filter = ('jornada', 'fecha_inicio')

    search_fields = ('trabajador__nombre', 'trabajador__apellido_paterno')
