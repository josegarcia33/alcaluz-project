from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from usuario import views as usuario_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuario/', include('usuario.urls')),
    #esta de abajo es para la página principal del sitio app
    path('', usuario_views.landing_page, name = 'landing')
]