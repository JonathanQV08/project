from django.urls import path
from .views import (
    PerfilUsuarioListView,
    PerfilUsuarioCreateView,
    PerfilUsuarioUpdateView,
    MiPerfilView
)

# Rutas principales de la app accounts
urlpatterns = [
    # Lista de perfiles (solo admin)
    path('perfiles/', PerfilUsuarioListView.as_view(), name='perfil_list'),

    # Crear nuevo perfil (solo admin)
    path('perfiles/nuevo/', PerfilUsuarioCreateView.as_view(), name='perfil_create'),

    # Editar perfil existente (solo admin)
    path('perfiles/<int:pk>/editar/', PerfilUsuarioUpdateView.as_view(), name='perfil_update'),

    # Ver el propio perfil
    path('mi-perfil/', MiPerfilView.as_view(), name='mi_perfil'),
]
