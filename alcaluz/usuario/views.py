
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login, authenticate
from usuario.forms import RegistroUsuarioForm, LoginForm, ZonaForm, RedForm
from usuario.models import Zona, Red
from .models import Luminaria, Red, RegistroConsumo
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime
#para lo de la pagina cero o página principal del app
def landing_page(current_request):
    if current_request.user.is_authenticated:
        return redirect('usuario:redirect_by_role')
    return render(current_request, 'landing.html')


def login_view(current_request):
    if current_request.user.is_authenticated:
        return redirect('usuario:redirect_by_role')
        
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
                error_message = "los datos son incorrectos, intente de nuevo"
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
    # Obtenemos las zonas con una consulta optimizada trayendo su municipio de un solo golpe
    zonas = Zona.objects.select_related('municipio').all().order_by('-id_zona')
    
    if current_request.method == 'POST':
        form = ZonaForm(current_request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario:registrar_zona')
    else:
        form = ZonaForm()
        
    return render(current_request, 'municipal/registrar_zona.html', {
        'form': form, 
        'zonas': zonas
    })


@login_required(login_url='usuario:login')
def registrar_red(current_request):
    # Obtenemos las redes y su cadena de relaciones hacia atrás
    redes = Red.objects.select_related('zona__municipio').all()
    
    if current_request.method == 'POST':
        form = RedForm(current_request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario:registrar_red')
    else:
        form = RedForm()
        
    return render(current_request, 'municipal/registrar_red.html', {'form': form, 'redes': redes})

def inicio(request):
    contexto = datos_formulario()
    contexto['form'] = ZonaForm()
    contexto['form_red'] = RedForm()
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
                contexto['form_zona'] = form
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
            contexto['error_consumo'] = 'La fecha de inicio debe ser anterior a la fecha de fin.'
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
        return redirect('registrar_luminaria')

    return render(request, 'municipal/registros.html', datos_formulario())


def datos_formulario():
    zonas = Zona.objects.select_related('municipio').all().order_by('-id_zona')
    redes = Red.objects.all()
    luminarias = Luminaria.objects.select_related('red').all()
    consumos = RegistroConsumo.objects.select_related('luminaria', 'tecnico').all()

    return {
        'zonas': zonas,
        'redes': redes,
        'luminarias': luminarias,
        'tecnicos': User.objects.filter(groups__name='Técnico'),
        'consumos': consumos,
        'zonas_count': zonas.count(),
        'redes_count': redes.count(),
        'luminarias_count': luminarias.count(),
        'consumos_count': consumos.count(),
    }
