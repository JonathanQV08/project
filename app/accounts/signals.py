from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Cada vez que se crea un nuevo User, se genera automáticamente un PerfilUsuario.
    Esto asegura que todo usuario tenga un perfil sin intervención manual.
    Se usa get_or_create para evitar duplicados cuando hay migraciones o usuarios creados por scripts.
    """
    if created:
        PerfilUsuario.objects.get_or_create(user=instance)
