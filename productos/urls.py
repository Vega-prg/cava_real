from django.urls import path
from .views import ListaProductosView , DetalleProductoView

urlpatterns = [
    path('', ListaProductosView.as_view(), name='lista_productos'),
    path('<slug:slug>/', DetalleProductoView.as_view(), name='detalle_producto'),
]