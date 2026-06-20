from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login, authenticate
from usuario.forms import RegistroUsuarioForm, LoginForm, ZonaForm, RedForm
from usuario.models import Zona, Red, Luminaria, RegistroConsumo, Reporte, Municipio

from .models import Luminaria, Red, RegistroConsumo
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime
#para lo de la pagina cero o página principal del app
def landing_page(current_request):

    return render(current_request, 'landing.html')


def login_view(current_request):
 
        
    error_message = None
    if current_request.method == 'POST':
        form = LoginForm(current_request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(current_request, username=username, password=password)
            if user is not None:
                auth_login(current_request, user)
                return redirect('usuario:redirect_by_role')
            else:
                messages.error(current_request, "Los datos son incorrectos, intente de nuevo")
    else:
        form = LoginForm()
        
    return render(current_request, 'registration/login.html', {'form': form, 'error_message': error_message})

# para técnicos es una pantalla, para un amin es otra
@login_required
def redirect_by_role(current_request):
    if current_request.user.groups.filter(name='Administrador').exists() or current_request.user.is_superuser:
        return redirect('usuario:admin_dashboard')
    elif current_request.user.groups.filter(name='Técnico').exists():
        return redirect('usuario:tecnico_dashboard')
    
## para la parte del registro de nuevos usuarios para el sistema 
def registro_usuario(current_request):
    # Si el usuario ya está logueado, lo mandamos a su pantalla
    if current_request.user.is_authenticated:
        return redirect('usuario:redirect_by_role')
        
    if current_request.method == 'POST':
        form = RegistroUsuarioForm(current_request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(current_request, user)
            return redirect('usuario:redirect_by_role')
    else:
        form = RegistroUsuarioForm()
        
    return render(current_request, 'registration/registro.html', {'form': form})
    return redirect('usuario:dashboard')

def es_administrador(user):
    return user.groups.filter(name='Administrador').exists() or user.is_superuser

def es_tecnico(user):
    return user.groups.filter(name='Técnico').exists()

# 2. Vistas de los Dashboards
@login_required
def dashboard_general(current_request):
    return render(current_request, 'account/dashboard.html', {'rol': 'Usuario General'})
# Dashboards protegidos - CORREGIDOS CON 'usuario:login'
@login_required(login_url='usuario:login')
@user_passes_test(es_administrador, login_url='usuario:login')
def admin_dashboard(current_request):
    return render(current_request, 'account/dashboard.html', {'rol': 'Administrador'})

@login_required(login_url='usuario:login')
@user_passes_test(es_tecnico, login_url='usuario:login')
def tecnico_dashboard(current_request):
    return render(current_request, 'account/dashboard.html', {'rol': 'Técnico'})


@login_required(login_url='usuario:login')
def registrar_zona(current_request):
    zonas = Zona.objects.select_related('municipio').all().order_by('-id_zona')
    redes = Red.objects.select_related('zona__municipio').all().order_by('-id_red')
    luminarias = Luminaria.objects.select_related('red').all()
    consumos = RegistroConsumo.objects.select_related('luminaria__red__zona', 'tecnico').all()
    tecnicos = User.objects.filter(groups__name='Técnico')
    municipios = Municipio.objects.all()

    zonas_count = Zona.objects.count()
    redes_count = Red.objects.count()
    luminarias_count = Luminaria.objects.count()
    consumos_count = RegistroConsumo.objects.count()

    if current_request.method == 'POST':
        form = ZonaForm(current_request.POST)
        if form.is_valid():
            form.save()
            messages.success(current_request, "Zona registrada correctamente")
            return redirect('usuario:registrar_zona')
        # Si el form tiene errores, vuelve al formulario mostrando los errores
    else:
        form = ZonaForm()

    # SIEMPRE se llega aquí si no hubo redirect (GET o POST con error)
    return render(current_request, 'municipal/registros.html', {
        'form': form,
        'form_red': RedForm(),
        'zonas': zonas,
        'redes': redes,
        'municipios': municipios,
        'luminarias': luminarias,
        'consumos': consumos,
        'tecnicos': tecnicos,
        'zonas_count': zonas_count,
        'redes_count': redes_count,
        'luminarias_count': luminarias_count,
        'consumos_count': consumos_count,
        'pagina_activa': 'reg-zonas',   # ← SIEMPRE presente
    })
       
        
    


@login_required(login_url='usuario:login')
def registrar_red(current_request):
    zonas = Zona.objects.select_related('municipio').all().order_by('-id_zona')
    redes = Red.objects.select_related('zona__municipio').all().order_by('-id_red')
    luminarias = Luminaria.objects.select_related('red').all()
    consumos = RegistroConsumo.objects.select_related('luminaria__red__zona', 'tecnico').all()
    tecnicos = User.objects.filter(groups__name='Técnico')
    municipios = Municipio.objects.all().order_by('nombre')
    zonas_count = Zona.objects.count()
    redes_count = Red.objects.count()
    luminarias_count = Luminaria.objects.count()
    consumos_count = RegistroConsumo.objects.count()

    if current_request.method == 'POST':
        form_red = RedForm(current_request.POST)
        if form_red.is_valid():
            form_red.save()
            messages.success(current_request, "Red registrada correctamente")
            return redirect('usuario:registrar_red')
    else:
        form_red = RedForm()

    return render(current_request, 'municipal/registros.html', {
        'form': ZonaForm(),
        'form_red': form_red,
        'zonas': zonas,
        'redes': redes,
        'luminarias': luminarias,
        'municipios': municipios,
        'consumos': consumos,
        'tecnicos': tecnicos,
        'zonas_count': zonas_count,
        'redes_count': redes_count,
        'luminarias_count': luminarias_count,
        'consumos_count': consumos_count,
        'pagina_activa': 'reg-redes',   # ← SIEMPRE presente
    })

import io
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

@login_required(login_url='usuario:login')
@user_passes_test(es_administrador, login_url='usuario:login')
def generar_reporte_consumo(current_request):
    # Datos para los filtros de la interfaz visual
    zonas = Zona.objects.all()
    redes = Red.objects.all()
    luminarias = Luminaria.objects.all()

    # Filtro por defecto
    registros = RegistroConsumo.objects.select_related('luminaria__red__zona').all().order_by('-fecha_registro')

    # Si el usuario presiona el botón azul "Generar y Descargar" (Petición POST)
    if current_request.method == 'POST':
        tipo_nivel = current_request.POST.get('tipo_nivel', '') 
        fecha_inicio = current_request.POST.get('fecha_inicio')
        fecha_fin = current_request.POST.get('fecha_fin')
        
        
        luminaria_id = current_request.POST.get('luminaria_id')
        zona_id = current_request.POST.get('zona_id')
        red_id = current_request.POST.get('red_id')

        
        registros_filtrados = registros.filter(fecha_registro__range=[fecha_inicio, fecha_fin])
        
        
        if tipo_nivel == 'luminaria' and luminaria_id:
            registros_filtrados = registros_filtrados.filter(luminaria__id_luminaria=luminaria_id)
            titulo_reporte = f"REPORTE DE LUMINARIA ESPECÍFICA (ID: #{Luminaria.objects.get(id_luminaria=luminaria_id).id_luminaria})"
            
        elif tipo_nivel == 'red' and red_id:
            
            registros_filtrados = registros_filtrados.filter(luminaria__red__id_red=red_id)
            red_obj = Red.objects.get(id_red=red_id)
            titulo_reporte = f"REPORTE DE RED ELÉCTRICA ({red_obj.nombre.upper()})"
            
        elif tipo_nivel == 'zona' and zona_id:
            
            registros_filtrados = registros_filtrados.filter(luminaria__red__zona__id_zona=zona_id)
            zona_obj = Zona.objects.get(id_zona=zona_id)
            titulo_reporte = f"REPORTE DE ZONA ({zona_obj.nombre.upper()})"
            
        else:
            
            titulo_reporte = "REPORTE DE CONSUMO ENERGÉTICO MUNICIPAL (GENERAL)"

        # Cálculos matemáticos
        total_kwh = sum(r.consumo_kwh for r in registros_filtrados)
        total_costo = sum(r.costo for r in registros_filtrados)
        total_luminarias = registros_filtrados.values('luminaria').distinct().count()

        # --- ARQUITECTURA DEL REPORTE PDF ---
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter,
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
        )
        story = []
        styles = getSampleStyleSheet()

        titulo_style = ParagraphStyle(
            'TituloReporte', parent=styles['Heading1'],
            fontSize=22, leading=26, textColor=colors.HexColor('#1e293b'), alignment=1, spaceAfter=10
        )
        sub_style = ParagraphStyle(
            'SubTituloReporte', parent=styles['Normal'],
            fontSize=10, leading=14, textColor=colors.HexColor('#64748b'), alignment=1, spaceAfter=20
        )
        meta_style = ParagraphStyle(
            'MetaReporte', parent=styles['Normal'],
            fontSize=11, leading=16, textColor=colors.HexColor('#334155')
        )

        # Encabezado
        story.append(Paragraph("SISTEMA ALCA-LUZ", titulo_style))
        story.append(Paragraph(titulo_reporte, ParagraphStyle('Sub', parent=titulo_style, fontSize=13, textColor=colors.HexColor('#2563eb'))))
        story.append(Paragraph(f"Período auditado: del {fecha_inicio} al {fecha_fin}", sub_style))
        story.append(Spacer(1, 10))

        # Resumen
        resumen_data = [
            [Paragraph("<b>Métrica General</b>", meta_style), Paragraph("<b>Valor Calculado</b>", meta_style)],
            ["Luminarias Auditadas:", f"{total_luminarias} unidades"],
            ["Consumo Total Acumulado:", f"{total_kwh:.2f} kWh"],
            ["Costo Total Estimado:", f"${total_costo:.2f} USD"],
        ]
        tabla_resumen = Table(resumen_data, colWidths=[250, 250])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#f1f5f9')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        story.append(Paragraph("<b>1. Resumen Consolidado</b>", ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, spaceAfter=8)))
        story.append(tabla_resumen)
        story.append(Spacer(1, 20))

        # Tabla Detalles
        story.append(Paragraph("<b>2. Desglose Detallado de Registros</b>", ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, spaceAfter=8)))
        tabla_data = [["Luminaria ID", "Red Eléctrica", "Zona", "Consumo (kWh)", "Costo (USD)"]]
        for r in registros_filtrados:
            tabla_data.append([
                f"#{r.luminaria.id_luminaria}",
                r.luminaria.red.nombre,
                r.luminaria.red.zona.nombre,
                f"{r.consumo_kwh:.2f}",
                f"${r.costo:.2f}"
            ])
            
        tabla_detalles = Table(tabla_data, colWidths=[80, 110, 130, 90, 90])
        tabla_detalles.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        story.append(tabla_detalles)

        # Retornar PDF
        doc.build(story)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"Reporte_ALCA_LUZ_{tipo_nivel}.pdf")

    # Petición GET
    context = {
        'zonas': zonas,
        'redes': redes,
        'luminarias': luminarias,
        'registros': registros,
    }
    return render(current_request, 'municipal/reporte_consumo.html', context)
def inicio(request):
    contexto = datos_formulario()
    contexto['form'] = ZonaForm()
    contexto['form_red'] = RedForm()
    contexto['pagina_activa'] = 'dashboard' 
    return render(request, 'municipal/registros.html', contexto)




def registrar_luminaria(request):
    if request.method == 'POST':
        # Verificar si es un registro de zona
        if 'nombre' in request.POST and 'municipio' in request.POST:
            form = ZonaForm(request.POST)
            if form.is_valid():
                form.save()                      
                return redirect('usuario:registrar_luminaria')
            else:
                contexto = datos_formulario()
                contexto['form'] = form
                contexto['form_red'] = RedForm()
                contexto['pagina_activa'] = 'reg-zonas'
                return render(request, 'municipal/registros.html', contexto)        # Verificar si es un registro de red
        if 'nombre' in request.POST and 'zona' in request.POST and 'municipio' not in request.POST:
            form_red = RedForm(request.POST)
            if form_red.is_valid():
                form_red.save()
                return redirect('usuario:registrar_luminaria')
            else:
                contexto = datos_formulario()
                contexto['form'] = ZonaForm()
                contexto['form_red'] = form_red
                contexto['pagina_activa'] = 'reg-redes'
                return render(request, 'municipal/registros.html', contexto)
        # Registro de luminaria
        if 'potencia' in request.POST and 'red' in request.POST:
            Luminaria.objects.create(
                potencia = request.POST['potencia'],
                ubicacion = request.POST['ubicacion'],
                fecha_instalacion = request.POST['fecha_instalacion'],
                red_id = request.POST['red']
             )
            messages.success(request, "Luminaria registrada correctamente")
            return redirect('usuario:registrar_luminaria')
       
    
    contexto = datos_formulario()
    contexto['form'] = ZonaForm()
    contexto['form_red'] = RedForm()
    return render(request, 'municipal/registros.html', contexto)


def registrar_consumo(request):
    if request.method == 'POST':
        luminaria = request.POST.get('luminaria')
        consumo = request.POST.get('consumo_kwh')
        periodo_inicio = request.POST.get('periodo_inicio')
        periodo_fin = request.POST.get('periodo_fin')
        tecnico = request.POST.get('tecnico')

        if not luminaria or not consumo or not periodo_inicio or not periodo_fin or not tecnico:
            contexto = datos_formulario()
            contexto['error_consumo'] = 'Debe completar todos los campos del registro de consumo.'
            return render(request, 'municipal/registros.html', contexto)

        fecha_inicio = datetime.strptime(periodo_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(periodo_fin, '%Y-%m-%d').date()

        if fecha_inicio >= fecha_fin:
            contexto = datos_formulario()
            contexto['pagina_activa'] = 'reg-consumo'
            messages.error(request, "La fecha de inicio debe ser anterior a la fecha de fin.")
            return render(request, 'municipal/registros.html', contexto)

        consumo_kwh = Decimal(consumo)
        costo = consumo_kwh * Decimal('0.10')

        RegistroConsumo.objects.create(
            periodo_inicio=fecha_inicio,
            periodo_fin=fecha_fin,
            luminaria_id=luminaria,
            tecnico_id=tecnico,
            consumo_kwh=consumo_kwh,
            costo=costo
        )
        messages.success(request, "Consumo registrado correctamente")
        return redirect('usuario:registrar_luminaria')

    return render(request, 'municipal/registros.html', datos_formulario())


def datos_formulario():
    zonas = Zona.objects.select_related('municipio').all().order_by('-id_zona')
    redes = Red.objects.all()
    luminarias = Luminaria.objects.select_related('red').all()
    consumos = RegistroConsumo.objects.select_related('luminaria', 'tecnico').all()
    municipios = Municipio.objects.all().order_by('nombre')
    return {
        'zonas': zonas,
        'redes': redes,
        'luminarias': luminarias,
        'municipios': municipios,
        'tecnicos': User.objects.filter(groups__name='Técnico'),
        'consumos': consumos,
        'zonas_count': zonas.count(),
        'redes_count': redes.count(),
        'luminarias_count': luminarias.count(),
        'consumos_count': consumos.count(),
    }
