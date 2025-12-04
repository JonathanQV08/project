# incidents/urls.py
# Rutas para incidencias

from django.urls import path
from . import views

app_name = 'incidents'

urlpatterns = [
    # Admin / Jefe
    path('', views.IncidenciaListView.as_view(), name='incidencia_list'),
    path('nueva/', views.IncidenciaCreateView.as_view(), name='incidencia_create'),
    path('<int:pk>/editar/', views.IncidenciaUpdateView.as_view(), name='incidencia_update'),
    path('<int:pk>/', views.IncidenciaDetailView.as_view(), name='incidencia_detail'),

    # Trabajador
    path('mis-incidencias/', views.MisIncidenciasListView.as_view(), name='mis_incidencias'),
    path('solicitar/', views.NuevaIncidenciaTrabajadorView.as_view(), name='incidencia_trabajador_create'),
]
