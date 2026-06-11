from django.shortcuts import redirect, render
from .models import Luminaria, Red, RegistroConsumo
from django.contrib.auth.models import User
from decimal import Decimal
def inicio(request):
    return render(request, 'municipal/registrar_luminYconsumo.html')




def registrar_luminaria(request):
    if request.method == 'POST':
        Luminaria.objects.create(
            potencia = request.POST['potencia'],
            ubicacion = request.POST['ubicacion'],
            fecha_instalacion = request.POST['fecha_instalacion'],
            red_id = request.POST['red']
         )
        return redirect('registrar_luminaria')
       
    
    redes = Red.objects.all()
    luminarias = Luminaria.objects.select_related('red').all()
    tecnicos = User.objects.filter(groups__name='Técnico')
    
    return render(request, 'municipal/registrar_luminYconsumo.html', datos_formulario())


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
            return render(request, 'municipal/registrar_luminYconsumo.html', contexto)

        consumo_kwh = Decimal(consumo)
        costo = consumo_kwh * Decimal('0.10')

        RegistroConsumo.objects.create(
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
            luminaria_id=luminaria,
            tecnico_id=tecnico,
            consumo_kwh=consumo_kwh,
            costo=costo
        )
        return redirect('registrar_luminaria')

    return render(request, 'municipal/registrar_luminYconsumo.html', datos_formulario())

def datos_formulario():
    return {
        'redes': Red.objects.all(),
        'luminarias': Luminaria.objects.select_related('red').all(),
        'tecnicos': User.objects.filter(groups__name='Técnico'),
        'consumos': RegistroConsumo.objects.select_related('luminaria', 'tecnico').all(),
    }