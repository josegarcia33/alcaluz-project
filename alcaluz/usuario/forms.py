from django import forms

from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username= forms.CharField()
    password= forms.CharField(widget=forms.PasswordInput)


class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username'] 

    # Modificamos el guardado para asignar el rol de Técnico de forma automática
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Buscamos el grupo Técnico y lo vinculamos al nuevo usuario
            grupo_tecnico, _ = Group.objects.get_or_create(name='Técnico')
            user.groups.add(grupo_tecnico)
        return user