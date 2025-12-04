from django.db import models
from core.audit import AuditMixin
from core.models import UnidadAdministrativa, Puesto, TipoNombramiento
from django.core.validators import RegexValidator

class Trabajador(AuditMixin, models.Model):
    """
    Tabla 4: Trabajador
    Información personal, fiscal y laboral del empleado.
    """
    nombre = models.CharField(max_length=100, verbose_name="Nombre(s)", null=True, blank=True)
    apellido_paterno = models.CharField(max_length=100, verbose_name="Apellido Paterno", null=True, blank=True)
    apellido_materno = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Apellido Materno"
    )

    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        verbose_name="Correo Electrónico"
    )

    # Información Administrativa
    numero_empleado = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="No. Empleado",
        null=True,
        blank=True
    )

    rfc = models.CharField(
        max_length=13, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$',
                message='RFC inválido'
            )
        ],
        null=True,
        blank=True
    )

    curp = models.CharField(
        max_length=18,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]\d$',
                message='CURP inválido'
            )
        ],
        null=True,
        blank=True
    )
    
    # Relaciones (Foreign Keys a Core)
    unidad = models.ForeignKey(
        UnidadAdministrativa,
        on_delete=models.PROTECT,
        verbose_name="Unidad de Adscripción",
        null=True,
        blank=True
    )
    puesto = models.ForeignKey(
        Puesto,
        on_delete=models.PROTECT,
        verbose_name="Puesto Actual",
        null=True,
        blank=True
    )
    tipo_nombramiento = models.ForeignKey(
        TipoNombramiento,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Nombramiento",
        null=True,
        blank=True
    )

    # Estado
    activo = models.BooleanField(
        default=True,
        verbose_name="¿Trabajador Activo?"
    )

    fecha_ingreso = models.DateField(
        auto_now_add=True,
        null=True,   # necesario para migraciones sin default
        blank=True
    )

    def __str__(self):
        return f"{self.nombre or ''} {self.apellido_paterno or ''} ({self.numero_empleado or 'S/E'})"

    class Meta:
        verbose_name = "Trabajador"
        verbose_name_plural = "Trabajadores"
        ordering = ['apellido_paterno', 'nombre']

class JornadaLaboral(AuditMixin, models.Model):
    """
    Tabla 8: Jornada Laboral
    Define los horarios base y los días laborables.
    """
    descripcion = models.CharField(
        max_length=100,
        verbose_name="Nombre del Turno",
        help_text="Ej: Matutino A",
        null=True,
        blank=True
    )
    hora_entrada = models.TimeField(
        verbose_name="Hora de Entrada",
        null=True,
        blank=True
    )
    hora_salida = models.TimeField(
        verbose_name="Hora de Salida",
        null=True,
        blank=True
    )
    dias_semana = models.CharField(
        max_length=50,
        verbose_name="Días laborables",
        help_text="Ej: Lunes a Viernes (L-V)",
        null=True,
        blank=True
    )

    def __str__(self):
        if self.hora_entrada and self.hora_salida:
            return f"{self.descripcion} ({self.hora_entrada.strftime('%H:%M')} - {self.hora_salida.strftime('%H:%M')})"
        return self.descripcion or "Jornada sin nombre"

    class Meta:
        verbose_name = "Jornada Laboral"
        verbose_name_plural = "Jornadas Laborales"

class TrabajadorJornada(AuditMixin, models.Model):
    """
    Tabla 10: Asignación de Jornada
    Histórico de horarios asignados a un trabajador.
    """
    trabajador = models.ForeignKey(
        Trabajador,
        on_delete=models.CASCADE,
        related_name='jornadas',
        null=True,
        blank=True
    )
    jornada = models.ForeignKey(
        JornadaLaboral,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    fecha_inicio = models.DateField(
        verbose_name="Fecha de Inicio",
        null=True,
        blank=True
    )
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Fin",
        help_text="Dejar vacío si es el horario actual"
    )

    def __str__(self):
        return f"{self.trabajador} - {self.jornada}"

    class Meta:
        verbose_name = "Asignación de Jornada"
        verbose_name_plural = "Historial de Jornadas"
