from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from productos.models import Producto
from .models import Carrito, ItemCarrito
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import FormView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import DireccionEnvioForm
from .forms import MetodoPagoForm
from .models import Pedido, ItemPedido, DireccionEnvio, MetodoPago
from django.urls import reverse_lazy, reverse
from django.db import transaction
from .forms import SeleccionarMetodoPagoForm, SeleccionarDireccionForm
from django import forms





class CheckoutForm(forms.Form):
    direccion_id = forms.IntegerField(required=True)
    metodo_pago_id = forms.IntegerField(required=True)

class CheckoutUnificadoView(LoginRequiredMixin, FormView):
    template_name = 'checkout/unificado.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('confirmacion_pedido')

    def dispatch(self, request, *args, **kwargs):
        carrito = Carrito.objects.get(usuario=request.user)
        if not carrito.items.exists():
            return redirect('ver_carrito')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        
        context['direcciones'] = DireccionEnvio.objects.filter(usuario=usuario)
        context['metodos_pago'] = MetodoPago.objects.filter(usuario=usuario, activo=True)
        context['carrito'] = Carrito.objects.get(usuario=usuario)
        
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                usuario = self.request.user
                carrito = Carrito.objects.get(usuario=usuario)
                
                # Obtener dirección y método de pago seleccionados
                direccion = DireccionEnvio.objects.get(
                    id=form.cleaned_data['direccion_id'],
                    usuario=usuario
                )
                
                metodo_pago = MetodoPago.objects.get(
                    id=form.cleaned_data['metodo_pago_id'],
                    usuario=usuario,
                    activo=True
                )

                # Crear pedido
                pedido = Pedido.objects.create(
                    usuario=usuario,
                    direccion_envio=direccion,
                    metodo_pago=metodo_pago,
                    total=carrito.total
                )

                # Crear items y reducir stock
                for item in carrito.items.all():
                    ItemPedido.objects.create(
                        pedido=pedido,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio=item.producto.precio
                    )
                    item.producto.stock -= item.cantidad
                    item.producto.save()

                # Limpiar carrito
                carrito.items.all().delete()
                
                return super().form_valid(form)
                
        except Exception as e:
            messages.error(self.request, f"Error al procesar el pedido: {str(e)}")
            return redirect('checkout_unificado')

















class AgregarDireccionView(LoginRequiredMixin, CreateView):
    model = DireccionEnvio
    fields = ['direccion', 'ciudad', 'provincia', 'codigo_postal', 'telefono', 'instrucciones', 'default']
    template_name = 'carrito/agregar_direccion.html'
    
    def get_success_url(self):
        return self.request.GET.get('next', reverse('checkout_direccion'))  # Redirige al checkout o a donde venga de 'next'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        # Si se marca como default, desmarcar otras
        if form.cleaned_data['default']:
            DireccionEnvio.objects.filter(usuario=self.request.user, default=True).update(default=False)
        return super().form_valid(form)

class AgregarTarjetaView(LoginRequiredMixin, CreateView):
    model = MetodoPago
    fields = ['tipo', 'ultimos_digitos', 'default']
    template_name = 'carrito/agregar_tarjeta.html'
    
    def get_success_url(self):
        return self.request.GET.get('next', reverse('checkout_pago'))  # Redirige al checkout o a 'next'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ocultar campo 'ultimos_digitos' (se calculará automáticamente)
        form.fields['ultimos_digitos'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        # Si es tarjeta, guardar últimos 4 dígitos (simulado)
        if form.cleaned_data['tipo'] == 'TARJETA':
            form.instance.ultimos_digitos = '4242'  # Ejemplo. En producción, usar datos reales.
        # Si se marca como default, desmarcar otras
        if form.cleaned_data['default']:
            MetodoPago.objects.filter(usuario=self.request.user, default=True).update(default=False)
        return super().form_valid(form)
    

class CheckoutPagoView(LoginRequiredMixin, FormView):
    template_name = 'checkout/pago.html'
    form_class = SeleccionarMetodoPagoForm  # Nuevo formulario
    success_url = reverse_lazy('confirmacion_pedido')

    def dispatch(self, request, *args, **kwargs):
        if 'direccion_id' not in request.session:
            return redirect('checkout_direccion')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user  # Pasar usuario al formulario
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carrito'] = Carrito.objects.get(usuario=self.request.user)
        context['direccion'] = DireccionEnvio.objects.get(id=self.request.session['direccion_id'])
        context['puede_agregar_tarjeta'] = True  # Habilitar botón "Agregar nueva tarjeta"
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        carrito = Carrito.objects.get(usuario=self.request.user)
        direccion = DireccionEnvio.objects.get(id=self.request.session['direccion_id'])
        metodo_pago = form.cleaned_data['metodo_pago']  # Método seleccionado (existente o nuevo)

        # Crear pedido (misma lógica que antes)
        pedido = Pedido.objects.create(
            usuario=self.request.user,
            direccion_envio=direccion,
            metodo_pago=metodo_pago,
            total=carrito.total
        )

        # Reducir stock y limpiar carrito
        for item in carrito.items.all():
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio=item.producto.precio
            )
            item.producto.stock -= item.cantidad
            item.producto.save()

        carrito.items.all().delete()
        del self.request.session['direccion_id']

        return super().form_valid(form)
    

class CheckoutDireccionView(LoginRequiredMixin, FormView):
    template_name = 'checkout/direccion_envio.html'
    form_class = SeleccionarDireccionForm  # Nuevo formulario (se explica abajo)
    success_url = reverse_lazy('checkout_unificado')

    def dispatch(self, request, *args, **kwargs):
        carrito = Carrito.objects.get(usuario=request.user)
        if not carrito.items.exists():
            return redirect('ver_carrito')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user  # Pasar usuario al formulario
        return kwargs

    def form_valid(self, form):
        # Guardar ID de la dirección seleccionada en sesión
        direccion = form.cleaned_data['direccion']
        self.request.session['direccion_id'] = direccion.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_agregar_direccion'] = True  # Habilitar botón "Agregar nueva"
        return context

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, disponible=True)
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    
    # Obtener la cantidad del formulario
    cantidad = int(request.POST.get('cantidad', 1))
    
    # Validar que la cantidad sea válida
    if cantidad < 1 or cantidad > producto.stock:
        messages.error(request, "Cantidad no válida.")
        return redirect('detalle_producto', slug=producto.slug)
    
    item, created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': cantidad}
    )
    
    if not created:
        nueva_cantidad = item.cantidad + cantidad
        if nueva_cantidad <= producto.stock:
            item.cantidad = nueva_cantidad
            item.save()
            messages.success(request, f"Se agregaron {cantidad} unidades de {producto.nombre}")
        else:
            messages.warning(request, "No hay suficiente stock disponible.")
    else:
        messages.success(request, f"{producto.nombre} fue agregado al carrito ({cantidad} unidades)")
    
    return redirect('detalle_producto', slug=producto.slug)

@login_required
def ver_carrito(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    return render(request, 'carrito/carrito.html', {'carrito': carrito})

@require_POST
@login_required
def actualizar_cantidad(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    nueva_cantidad = int(request.POST.get('cantidad', 1))
    
    if 1 <= nueva_cantidad <= item.producto.stock:
        item.cantidad = nueva_cantidad
        item.save()
        messages.success(request, "Cantidad actualizada")
    else:
        messages.error(request, "Cantidad no válida")
    
    return redirect('ver_carrito')

@login_required
def eliminar_item(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    messages.success(request, "Producto eliminado del carrito")
    return redirect('ver_carrito')