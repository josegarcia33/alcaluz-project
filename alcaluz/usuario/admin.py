from django.contrib import admin
from .models import Departamento, Municipio, Zona, Red, Luminaria, RegistroConsumo, Reporte

# Registramos todas las tablas estructurales
admin.site.register(Departamento)
admin.site.register(Municipio)
admin.site.register(Zona)
admin.site.register(Red)
admin.site.register(Luminaria)
admin.site.register(RegistroConsumo)
admin.site.register(Reporte)