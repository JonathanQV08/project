from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    """
    Extiende el modelo User de Django para asignar un rol dentro del sistema.
    También permite vincular opcionalmente un trabajador cuando exista la app workers.
    """

    # Opciones de rol disponibles dentro del sistema
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('JEFE', 'Jefe de área'),
        ('TRAB', 'Trabajador'),
    ]

    # Relación uno a uno con el modelo User (perfil extendido)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Rol asignado al usuario
    rol = models.CharField(max_length=10, choices=ROLE_CHOICES, default='TRAB')

    # Relación opcional con un trabajador (cuando exista la app workers)
    trabajador = models.OneToOneField(
        'workers.Trabajador',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        """Representación legible del perfil."""
        return f"{self.user.username} - {self.get_rol_display()}"

    # Métodos utilitarios para verificar permisos por rol
    def es_admin(self):
        return self.rol == 'ADMIN'

    def es_jefe(self):
        return self.rol == 'JEFE'

    def es_trabajador(self):
        return self.rol == 'TRAB'
