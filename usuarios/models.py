from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date

class Usuario(AbstractUser):
    # Campos adicionales
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    GENERO_OPCIONES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    genero = models.CharField(max_length=1, choices=GENERO_OPCIONES)
    email = models.EmailField(unique=True)  # Email único

    # Método para calcular edad
    def edad(self):
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

    def es_mayor_de_edad(self):
        return self.edad() >= 18

    def __str__(self):
        return f"{self.nombre} {self.apellido}"