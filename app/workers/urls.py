from django.urls import path
from . import views

app_name = 'workers'

urlpatterns = [
    # Rutas para Trabajadores
    path('', views.TrabajadorListView.as_view(), name='trabajador_list'),
    path('nuevo/', views.TrabajadorCreateView.as_view(), name='trabajador_create'),
    path('<int:pk>/', views.TrabajadorDetailView.as_view(), name='trabajador_detail'),
    path('<int:pk>/editar/', views.TrabajadorUpdateView.as_view(), name='trabajador_update'),
    path('<int:pk>/eliminar/', views.TrabajadorDeleteView.as_view(), name='trabajador_delete'),
    
    # Rutas para Jornadas
    path('jornadas/', views.JornadaListView.as_view(), name='jornada_list'),
    path('jornadas/nueva/', views.JornadaCreateView.as_view(), name='jornada_create'),
    path('jornadas/<int:pk>/editar/', views.JornadaUpdateView.as_view(), name='jornada_update'),
    path('jornadas/<int:pk>/eliminar/', views.JornadaDeleteView.as_view(), name='jornada_delete'),

    # Asignación
    path('asignar-horario/', views.AsignarJornadaCreateView.as_view(), name='asignar_jornada'),
]