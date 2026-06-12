from django import forms
from usuario.models import Red, Zona
 
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
 
 
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
 
 
class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']
 
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            grupo_tecnico, _ = Group.objects.get_or_create(name='Técnico')
            user.groups.add(grupo_tecnico)
        return user
 
class ZonaForm(forms.ModelForm):
    class Meta:
        model = Zona
        fields = ['nombre', 'municipio', 'tipo_zona']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Colonia Escalón o Parque Central'}),
            'municipio': forms.Select(attrs={'class': 'form-select'}),
            'tipo_zona': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Urbana, rural, residencial...'}),
        }
 
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        municipio = cleaned_data.get('municipio')
 
        if nombre and municipio:
            if Zona.objects.filter(nombre__iexact=nombre, municipio=municipio).exists():
                raise forms.ValidationError(f"La zona '{nombre}' ya está registrada en este municipio.")
        return cleaned_data
 
 
class RedForm(forms.ModelForm):
    class Meta:
        model = Red
        fields = ['nombre', 'zona']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Red de Distribución Norte-1'}),
            'zona': forms.Select(attrs={'class': 'form-select'}),
        }
 
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if Red.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError("Ya existe una red eléctrica registrada con este nombre.")
        return nombre