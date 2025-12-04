from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from incidents.models import Incidencia
from workers.models import Trabajador
from attendance.models import RegistroAsistencia
from core.models import CalendarioLaboral, TipoIncidencia

@login_required
def dashboard(request):
    """Vista principal del dashboard con estadísticas y gráficos por rol."""

    user = request.user
    perfil = user.perfilusuario
    hoy = timezone.now().date()

    # ============================================
    # 0. Día inhábil (Calendario Laboral)
    # ============================================
    dia_inhabil = CalendarioLaboral.objects.filter(
        fecha=hoy,
        es_inhabil=True
    ).first()

    # ============================================
    # 1. Total de trabajadores activos
    # ============================================
    if perfil.rol == 'JEFE':
        total_trabajadores = Trabajador.objects.filter(
            activo=True,
            unidad=perfil.trabajador.unidad
        ).count()
    else:  # ADMIN y otros
        total_trabajadores = Trabajador.objects.filter(activo=True).count()

    # ============================================
    # 2. Asistencias de hoy
    # ============================================
    if perfil.rol == 'JEFE':
        total_asistencias = RegistroAsistencia.objects.filter(
            fecha=hoy,
            trabajador__unidad=perfil.trabajador.unidad
        ).count()
    else:
        total_asistencias = RegistroAsistencia.objects.filter(
            fecha=hoy
        ).count()

    # ============================================
    # 3. Incidencias pendientes
    # ADMIN y JEFE deben ver solo lo correspondiente
    # ============================================
    if perfil.rol == 'JEFE':
        total_incidencias = Incidencia.objects.filter(
            estatus='PENDIENTE',                 
            trabajador__unidad=perfil.trabajador.unidad
        ).count()
    else:
        total_incidencias = Incidencia.objects.filter(
            estatus='PENDIENTE'                
        ).count()

    # ============================================
    # 4. Gráfica semanal de asistencia
    # ============================================
    from datetime import timedelta

    semana_seleccionada = request.GET.get('semana', 'esta_semana')

    # Cálculo del rango semanal
    if semana_seleccionada == 'semana_pasada':
        inicio_semana_actual = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana_actual - timedelta(days=1)
        inicio_semana = fin_semana - timedelta(days=6)

    elif semana_seleccionada == 'hace_dos_semanas':
        inicio_semana_actual = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana_actual - timedelta(days=8)
        inicio_semana = fin_semana - timedelta(days=6)

    else:  # esta Semana
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=4)

    # Labels y datos
    dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie']
    chart_labels = []
    chart_data = []

    # Total trabajadores activos (según el rol):
    total_trabajadores_activos = (
        Trabajador.objects.filter(activo=True, unidad=perfil.trabajador.unidad).count()
        if perfil.rol == 'JEFE'
        else Trabajador.objects.filter(activo=True).count()
    )

    # Evitar división entre cero
    if total_trabajadores_activos == 0:
        chart_data = [0, 0, 0, 0, 0]
    else:
        for i in range(5):
            fecha_dia = inicio_semana + timedelta(days=i)
            chart_labels.append(f"{dias_semana[i]} {fecha_dia.day}/{fecha_dia.month}")

            if fecha_dia > hoy:
                chart_data.append(0)
                continue

            # Asistencias por rol
            if perfil.rol == 'JEFE':
                asistencias_dia = RegistroAsistencia.objects.filter(
                    fecha=fecha_dia,
                    trabajador__unidad=perfil.trabajador.unidad
                ).count()
            else:
                asistencias_dia = RegistroAsistencia.objects.filter(
                    fecha=fecha_dia
                ).count()

            porcentaje = round((asistencias_dia / total_trabajadores_activos) * 100, 1)
            chart_data.append(porcentaje)
        
    es_admin = perfil.rol == "ADMIN"
    es_jefe = perfil.rol == "JEFE"
    es_trabajador = perfil.rol == "TRAB"  # o el valor real que uses en choices

    context = {
        'total_trabajadores': total_trabajadores,
        'total_asistencias': total_asistencias,
        'total_incidencias': total_incidencias,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'semana_seleccionada': semana_seleccionada,
        'dia_inhabil': dia_inhabil,
        'es_admin': es_admin,
        'es_jefe': es_jefe,
        'es_trabajador': es_trabajador,
    }


    return render(request, 'dashboard.html', context)
