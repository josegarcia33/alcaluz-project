
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login, authenticate
from usuario.forms import RegistroUsuarioForm, LoginForm, ZonaForm, RedForm
from usuario.models import Zona, Red

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
    zonas = Zona.objects.select_related('municipio').all().order_by('-fecha_registro')
    
    if current_request.method == 'POST':
        form = ZonaForm(current_request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario:registrar_zona')
    else:
        form = ZonaForm()
        
    return render(current_request, 'municipal/registrar_zona.html', {'form': form, 'zonas': zonas})


@login_required(login_url='usuario:login')
def registrar_red(current_request):
    # Obtenemos las redes y su cadena de relaciones hacia atrás
    redes = Red.objects.select_related('zona__municipio').all().order_by('-fecha_registro')
    
    if current_request.method == 'POST':
        form = RedForm(current_request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario:registrar_red')
    else:
        form = RedForm()
        
    return render(current_request, 'municipal/registrar_red.html', {'form': form, 'redes': redes})