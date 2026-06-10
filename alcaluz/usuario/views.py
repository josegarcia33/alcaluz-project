from django.shortcuts import render

def inicio(request):
    return render(request, 'municipal/registrar_luminYconsumo.html')