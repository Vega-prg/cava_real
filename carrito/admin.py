from django.contrib import admin
from .models import DireccionEnvio, Carrito, ItemCarrito, Pedido, ItemPedido, MetodoPago



class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['producto', 'cantidad', 'precio']
    can_delete = False

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['numero_pedido', 'usuario', 'estado', 'total', 'creado_en']
    list_filter = ['estado', 'creado_en']
    search_fields = ['numero_pedido', 'usuario__username']
    inlines = [ItemPedidoInline]
    readonly_fields = ['numero_pedido', 'creado_en']
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_pedido', 'usuario', 'estado', 'total')
        }),
        ('Detalles de Envío y Pago', {
            'fields': ('direccion_envio', 'metodo_pago')
        }),
    )

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo', 'ultimos_digitos', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['usuario__username', 'ultimos_digitos']

@admin.register(DireccionEnvio)
class DireccionEnvioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'direccion', 'ciudad', 'provincia', 'default')
    list_filter = ('ciudad', 'provincia')
    search_fields = ('usuario__username', 'direccion')
    list_editable = ('default',)
    list_per_page = 20

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_creacion', 'total')
    readonly_fields = ('total',)
    search_fields = ('usuario__username',)

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'carrito', 'cantidad', 'subtotal')
    list_filter = ('carrito__usuario',)
    search_fields = ('producto__nombre',)