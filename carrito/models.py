from django.db import models
from usuarios.models import Usuario
from productos.models import Producto
from django.core.exceptions import ValidationError
import uuid
from django.core.validators import MinValueValidator



class MetodoPago(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=[('TARJETA', 'Tarjeta'), ('EFECTIVO', 'Efectivo')])
    ultimos_digitos = models.CharField(max_length=4, blank=True, null=True)  # Para tarjetas
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    default = models.BooleanField(default=False, verbose_name="Método principal")

    def save(self, *args, **kwargs):
        # Solo un método puede ser default por usuario
        if self.default:
            MetodoPago.objects.filter(usuario=self.usuario, default=True).update(default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} {'****' + self.ultimos_digitos if self.ultimos_digitos else ''}"

class Pedido(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('ENVIADO', 'Enviado'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]

    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT)
    numero_pedido = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    direccion_envio = models.ForeignKey('DireccionEnvio', on_delete=models.PROTECT)
    metodo_pago = models.ForeignKey('MetodoPago', on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.numero_pedido}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.precio * self.cantidad
    

class DireccionEnvio(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='direcciones')
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, verbose_name="Código Postal")
    telefono = models.CharField(max_length=15)
    instrucciones = models.TextField(blank=True, verbose_name="Instrucciones adicionales")
    creado_en = models.DateTimeField(auto_now_add=True)
    default = models.BooleanField(default=False, verbose_name="Dirección principal")

    def save(self, *args, **kwargs):
        # Solo una dirección puede ser default por usuario
        if self.default:
            DireccionEnvio.objects.filter(usuario=self.usuario, default=True).update(default=False)
        super().save(*args, **kwargs)
      
    class Meta:
        verbose_name = "Dirección de Envío"
        verbose_name_plural = "Direcciones de Envío"

    def __str__(self):
        return f"{self.direccion}, {self.ciudad}"

class Carrito(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='carrito')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad

    def clean(self):
        if self.cantidad > self.producto.stock:
            raise ValidationError("No hay suficiente stock disponible.")