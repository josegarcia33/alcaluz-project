from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuario'

urlpatterns = [
    # Login / Logout s
    #path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/',views.registro_usuario, name='registro' ),

    # otras rutas
    path('redirect/', views.redirect_by_role, name='redirect_by_role'),
    path('dashboard/', views.dashboard_general, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/tecnico/', views.tecnico_dashboard, name='tecnico_dashboard'),
    path('estructura/zona/',views.registrar_zona, name='registrar_zona'),
    path('estructura/red/', views.registrar_red, name='registrar_red'),
    path('reportes/consumo/', views.generar_reporte_consumo, name='generar_reporte_consumo'),
    path('registrar_luminYconsumo/', views.registrar_luminaria, name='registrar_luminaria'),
    path('registrar_consumo/', views.registrar_consumo, name='registrar_consumo'),
    path('', views.inicio, name='inicio'),
]