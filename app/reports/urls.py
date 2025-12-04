# reports/urls.py

from django.urls import path
from .views import (
    ReportesDashboardView,
    ReportePorTrabajadorView,
    ReportePorUnidadView,
    ReportePersonalView,
    exportar_csv_trabajador,
    exportar_csv_unidad
)

app_name = "reports"

urlpatterns = [
    path("", ReportesDashboardView.as_view(), name="dashboard_reportes"),
    path("trabajador/", ReportePorTrabajadorView.as_view(), name="rep_trabajador"),
    path("unidad/", ReportePorUnidadView.as_view(), name="rep_unidad"),
    path("personal/", ReportePersonalView.as_view(), name="rep_personal"),

    # Exportar CSV
    path("csv/trabajador/", exportar_csv_trabajador, name="csv_trabajador"),
    path("csv/unidad/", exportar_csv_unidad, name="csv_unidad"),
]
    