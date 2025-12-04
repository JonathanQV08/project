from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Página principal del módulo core
    path('', views.CoreDashboardView.as_view(), name='core_dashboard'),
    
    # URLs de Unidades Administrativas
    path('unidades/', views.UnidadListView.as_view(), name='unidad_list'),
    path('unidades/nueva/', views.UnidadCreateView.as_view(), name='unidad_create'),
    path('unidades/<int:pk>/editar/', views.UnidadUpdateView.as_view(), name='unidad_update'),
    path('unidades/<int:pk>/eliminar/', views.UnidadDeleteView.as_view(), name='unidad_delete'),

    # URLs de Puestos
    path('puestos/', views.PuestoListView.as_view(), name='puesto_list'),
    path('puestos/nuevo/', views.PuestoCreateView.as_view(), name='puesto_create'),
    path('puestos/<int:pk>/editar/', views.PuestoUpdateView.as_view(), name='puesto_update'),
    path('puestos/<int:pk>/eliminar/', views.PuestoDeleteView.as_view(), name='puesto_delete'),

    # URLs de Tipos de Nombramiento
    path('nombramientos/', views.TipoNombramientoListView.as_view(), name='nombramiento_list'),
    path('nombramientos/nuevo/', views.TipoNombramientoCreateView.as_view(), name='nombramiento_create'),
    path('nombramientos/<int:pk>/editar/', views.TipoNombramientoUpdateView.as_view(), name='nombramiento_update'),
    path('nombramientos/<int:pk>/eliminar/', views.TipoNombramientoDeleteView.as_view(), name='nombramiento_delete'),

    # URLs de Tipos de Incidencia
    path('tipos-incidencia/', views.TipoIncidenciaListView.as_view(), name='tipo_incidencia_list'),
    path('tipos-incidencia/nuevo/', views.TipoIncidenciaCreateView.as_view(), name='tipo_incidencia_create'),
    path('tipos-incidencia/<int:pk>/editar/', views.TipoIncidenciaUpdateView.as_view(), name='tipo_incidencia_update'),
    path('tipos-incidencia/<int:pk>/eliminar/', views.TipoIncidenciaDeleteView.as_view(), name='tipo_incidencia_delete'),

    # URLs de Calendario Laboral
    path('calendario/', views.CalendarioListView.as_view(), name='calendario_list'),
    path('calendario/nuevo/', views.CalendarioCreateView.as_view(), name='calendario_create'),
    path('calendario/<int:pk>/editar/', views.CalendarioUpdateView.as_view(), name='calendario_update'),
    path('calendario/<int:pk>/eliminar/', views.CalendarioDeleteView.as_view(), name='calendario_delete'),
]