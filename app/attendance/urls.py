# attendance/urls.py
# Rutas del módulo de asistencia

from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Lista general (Admin / Jefe)
    path('', views.AsistenciaListView.as_view(), name='asistencia_list'),

    # Crear / Editar (Admin / Jefe)
    path('nueva/', views.AsistenciaCreateView.as_view(), name='asistencia_create'),
    path('<int:pk>/editar/', views.AsistenciaUpdateView.as_view(), name='asistencia_update'),

    # Detalle
    path('<int:pk>/', views.AsistenciaDetailView.as_view(), name='asistencia_detail'),

    # Trabajador: registro personal y consulta
    path('marcar/', views.MiAsistenciaCreateView.as_view(), name='marcar_asistencia'),
    path('mis-asistencias/', views.MisAsistenciasListView.as_view(), name='mis_asistencias'),
]
