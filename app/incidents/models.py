# incidents/models.py
# Modelo de incidencias del trabajador (gestión completa)

from datetime import timedelta, date

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.audit import AuditMixin
from workers.models import Trabajador
from core.models import TipoIncidencia, CalendarioLaboral
from attendance.models import RegistroAsistencia


class Incidencia(AuditMixin, models.Model):
    """
    Incidencia asociada a un trabajador.
    Puede abarcar uno o varios días y se utiliza para justificar
    faltas y retardos (integración con RegistroAsistencia).
    """

    ESTATUS = [
        ('PENDIENTE', 'Pendiente de aprobación'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    trabajador = models.ForeignKey(
        Trabajador,
        on_delete=models.CASCADE,
        related_name='incidencias'
    )

    tipo = models.ForeignKey(
        TipoIncidencia,
        on_delete=models.PROTECT,
        related_name='incidencias'
    )

    # Rango de fechas (una sola fecha si inicio == fin)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    motivo = models.TextField(blank=True)

    estatus = models.CharField(
        max_length=20,
        choices=ESTATUS,
        default='PENDIENTE'
    )

    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias_creadas'
    )

    aprobada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias_aprobadas'
    )

    class Meta:
        verbose_name = "Incidencia"
        verbose_name_plural = "Incidencias"
        ordering = ['-fecha_inicio', 'trabajador']

    def __str__(self):
        return f"{self.trabajador} - {self.tipo} ({self.fecha_inicio} a {self.fecha_fin})"

    # --------------------------------------------------
    # Utilidades de rango de fechas
    # --------------------------------------------------

    def dias(self):
        """Itera día por día en el rango."""
        actual = self.fecha_inicio
        while actual <= self.fecha_fin:
            yield actual
            actual += timedelta(days=1)

    def es_dia_inhabil(self, fecha: date) -> bool:
        return CalendarioLaboral.objects.filter(
            fecha=fecha,
            es_inhabil=True
        ).exists()

    # --------------------------------------------------
    # Integración con RegistroAsistencia
    # --------------------------------------------------

    def aplicar_a_asistencia(self):
        """
        Para incidencias APROBADAS:
        - Crea o actualiza registros de asistencia en el rango de fechas.
        - Marca la incidencia en RegistroAsistencia (campo incidencia/tipo).
        """
        if self.estatus != 'APROBADA':
            return

        for dia in self.dias():
            # Opcional: puedes omitir días inhábiles
            # if self.es_dia_inhabil(dia):
            #     continue

            asistencia, created = RegistroAsistencia.objects.get_or_create(
                trabajador=self.trabajador,
                fecha=dia,
                defaults={
                    # sin horas, pero con incidencia
                    'hora_entrada': None,
                    'hora_salida': None,
                    'incidencia': self.tipo,
                },
            )

            # Si ya existía, solo aseguramos que tenga la incidencia
            asistencia.incidencia = self.tipo
            asistencia.save()

    def save(self, *args, **kwargs):
        # Normalizar: fecha_fin >= fecha_inicio
        if self.fecha_fin < self.fecha_inicio:
            self.fecha_fin = self.fecha_inicio

        es_nueva = self.pk is None
        estatus_anterior = None
        if not es_nueva:
            estatus_anterior = Incidencia.objects.get(pk=self.pk).estatus

        super().save(*args, **kwargs)

        # Aplicar integración solo si está aprobada y:
        # – es nueva, o
        # – cambió de estatus y ahora es APROBADA
        if self.estatus == 'APROBADA' and (es_nueva or estatus_anterior != 'APROBADA'):
            self.aplicar_a_asistencia()
