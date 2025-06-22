from django.db import models
from django.utils.text import slugify


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='productos/')
    stock = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    graduacion_alcoholica = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name="Graduación Alcohólica (%)"
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.nombre}-{self.id}")
        super().save(*args, **kwargs)

    def get_disponibilidad(self):
        return "Disponible" if self.disponible and self.stock > 0 else "Agotado"


    def __str__(self):
        return f"{self.nombre} (${self.precio})"