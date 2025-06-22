from django.views.generic import ListView, DetailView
from .models import Producto

class ListaProductosView(ListView):
    model = Producto
    template_name = 'productos/lista_productos.html'
    context_object_name = 'productos'
    paginate_by = 8  # 8 productos por página
    queryset = Producto.objects.filter(disponible=True)  # Solo productos disponibles

class DetalleProductoView(DetailView):
    model = Producto
    template_name = 'productos/detalle_producto.html'
    context_object_name = 'producto'
    slug_field = 'slug'  # Campo para buscar el producto
    slug_url_kwarg = 'slug'  # Nombre en la URL

    def get_queryset(self):
        return Producto.objects.filter(disponible=True)  # Solo productos disponibles