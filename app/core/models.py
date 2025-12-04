from django.db import models

from core.audit import AuditMixin

class UnidadAdministrativa(AuditMixin, models.Model):
    """
    Tabla 5: Unidad Administrativa
    Representa departamentos, academias, etc. Es jerárquica (una unidad puede pertenecer a otra).
    """
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Unidad")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    unidad_padre = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sub_unidades',
        verbose_name="Unidad Superior (Opcional)",
        help_text="Si esta unidad pertenece a otra (ej. Depto. Sistemas -> Subdirección Académica)"
    )

    def __str__(self):
        # Muestra la jerarquía en el texto (ej: "Dirección > Sistemas")
        if self.unidad_padre:
            return f"{self.unidad_padre.nombre} > {self.nombre}"
        return self.nombre

    class Meta:
        verbose_name = "Unidad Administrativa"
        verbose_name_plural = "Unidades Administrativas"

class Puesto(AuditMixin, models.Model):
    """
    Tabla 6: Puesto
    Define el cargo y el nivel jerárquico.
    """
    NIVEL_CHOICES = [
        ('DOCENTE', 'Docente'),
        ('ADMIN', 'Administrativo'),
        ('DIRECTIVO', 'Directivo'),
        ('APOYO', 'Apoyo a la Educación'),
    ]
    
    nombre_puesto = models.CharField(max_length=100, verbose_name="Nombre del Puesto")
    nivel = models.CharField(
        max_length=20, 
        choices=NIVEL_CHOICES, 
        verbose_name="Nivel Jerárquico"
    )

    def __str__(self):
        return f"{self.nombre_puesto} ({self.get_nivel_display()})"

    class Meta:
        verbose_name = "Puesto"
        verbose_name_plural = "Puestos"

class TipoNombramiento(AuditMixin, models.Model):
    """
    Tabla 7: TipoNombramiento
    Ejemplos: Base, Confianza, Interino.
    """
    descripcion = models.CharField(max_length=50, verbose_name="Tipo de Nombramiento")

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name = "Tipo de Nombramiento"
        verbose_name_plural = "Tipos de Nombramiento"
        
class TipoIncidencia(AuditMixin, models.Model):
    """
    Tabla 12: TipoIncidencia
    Ejemplos: Incapacidad, Permiso con goce, Comisión sindical.
    """
    descripcion = models.CharField(max_length=100, verbose_name="Tipo de Incidencia")

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name = "Tipo de Incidencia"
        verbose_name_plural = "Tipos de Incidencia"        
    
class CalendarioLaboral(AuditMixin, models.Model):
    """
    Tabla 9: Calendario Laboral
    Define días inhábiles (festivos, vacaciones).
    """
    fecha = models.DateField(unique=True, verbose_name="Fecha")
    es_inhabil = models.BooleanField(default=True, verbose_name="¿Es día inhábil?")
    descripcion = models.CharField(max_length=100, verbose_name="Motivo (ej. Año Nuevo)")

    def __str__(self):
        estado = "Inhábil" if self.es_inhabil else "Hábil"
        return f"{self.fecha} - {self.descripcion} ({estado})"

    class Meta:
        verbose_name = "Día de Calendario"
        verbose_name_plural = "Calendario Laboral"
        #ordering = ['-fecha']