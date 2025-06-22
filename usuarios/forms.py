from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from datetime import date

class RegistroForm(UserCreationForm):
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de Nacimiento"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'nombre', 'apellido', 'email', 'fecha_nacimiento', 'genero', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        edad = (date.today() - fecha).days // 365
        if edad < 18:
            raise forms.ValidationError("Debes tener al menos 18 años para registrarte.")
        return fecha
        