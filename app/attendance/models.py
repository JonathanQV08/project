# attendance/models.py

from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

from core.audit import AuditMixin
from workers.models import Trabajador, TrabajadorJornada
from core.models import CalendarioLaboral, TipoIncidencia


class RegistroAsistencia(AuditMixin, models.Model):
    """
    Tabla 11 (SCA-B123): Registro de Asistencia
    Incluye:
    - Entrada/salida
    - Cálculo de retardos
    - Faltas automáticas
    - Vinculación a jornada activa
    - Integración con días inhábiles e incidencias
    """

    ESTADOS = [
        ('NORMAL', 'Asistencia Normal'),
        ('RETARDO', 'Retardo'),
        ('FALTA', 'Falta'),
        ('JUSTIFICADA', 'Justificada por Incidencia'),
        ('INHABIL', 'Día Inhábil'),
    ]


    trabajador = models.ForeignKey(
        Trabajador,
        on_delete=models.CASCADE,
        related_name="asistencias"
    )

    fecha = models.DateField(default=timezone.now)
    hora_entrada = models.TimeField(null=True, blank=True)
    hora_salida = models.TimeField(null=True, blank=True)

    estatus = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='NORMAL'
    )

    minutos_retardo = models.PositiveIntegerField(default=0)
    horas_trabajadas = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )

    # Incidencia opcional: permiso, incapacidad, comisión sindical, etc.
    incidencia = models.ForeignKey(
        TipoIncidencia,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    
    class Meta:
        verbose_name = "Registro de Asistencia"
        verbose_name_plural = "Registros de Asistencia"
        ordering = ['-fecha', 'trabajador']
        unique_together = ('trabajador', 'fecha')  # evita duplicados

    # ------------------------------
    # MÉTODOS DE NEGOCIO
    # ------------------------------

    def __str__(self):
        return f"{self.trabajador} - {self.fecha} ({self.estatus})"

    # --- 1. Determinar si es día inhábil ---
    def es_inhabil(self):
        return CalendarioLaboral.objects.filter(
            fecha=self.fecha,
            es_inhabil=True
        ).exists()

    # --- 2. Obtener jornada vigente del trabajador ---
    def jornada_vigente(self):
        return TrabajadorJornada.objects.filter(
            trabajador=self.trabajador,
            fecha_inicio__lte=self.fecha
        ).filter(
            models.Q(fecha_fin__gte=self.fecha) |
            models.Q(fecha_fin__isnull=True)
        ).select_related("jornada").first()

    # --- 3. Cálculo de minutos de retardo ---
    def calcular_retardo(self, hora_entrada, hora_jornada):
        if not hora_entrada or not hora_jornada:
            return 0

        dif = (
            datetime.combine(self.fecha, hora_entrada) -
            datetime.combine(self.fecha, hora_jornada)
        )

        return max(0, int(dif.total_seconds() // 60))

    # --- 4. Cálculo de horas trabajadas ---
    def calcular_horas_trabajadas(self):
        if not self.hora_entrada or not self.hora_salida:
            return 0

        dif = (
            datetime.combine(self.fecha, self.hora_salida) -
            datetime.combine(self.fecha, self.hora_entrada)
        )

        return round(dif.total_seconds() / 3600, 2)

    # --- 5. Cálculo del estatus final ---
    def calcular_estatus(self):
        # Regla 1: Día inhábil siempre gana
        if self.es_inhabil():
            return "INHABIL"

        # Regla 2: Incidencia (permiso, incapacidad, etc)
        if self.incidencia:
            return "JUSTIFICADA"

        jornada = self.jornada_vigente()
        if not jornada:
            return "NORMAL"

        # Falta → no checó entrada
        if not self.hora_entrada:
            return "FALTA"

        # Retardo
        minutos = self.calcular_retardo(self.hora_entrada, jornada.jornada.hora_entrada)
        if minutos > 0:
            return "RETARDO"

        return "NORMAL"


    # --- 6. Override save() con toda la lógica integrada ---
    def save(self, *args, **kwargs):

        # Regla principal: Día inhábil → limpiar todo
        if self.es_inhabil():
            self.estatus = "INHABIL"
            self.minutos_retardo = 0
            self.horas_trabajadas = 0
            return super().save(*args, **kwargs)

        # Calcular retardo y horas
        jornada = self.jornada_vigente()

        if jornada and self.hora_entrada:
            self.minutos_retardo = self.calcular_retardo(
                self.hora_entrada, jornada.jornada.hora_entrada
            )
        else:
            self.minutos_retardo = 0

        self.horas_trabajadas = self.calcular_horas_trabajadas()

        # Estatus final
        self.estatus = self.calcular_estatus()

        return super().save(*args, **kwargs)
