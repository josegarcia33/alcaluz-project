from django.urls import path
from . import vistas

urlpatterns = [
    path('', vistas.inicio, name='inicio'),
]
