from django.urls import path
from . import views
from django.views.generic import TemplateView
from .views import AgregarDireccionView, AgregarTarjetaView, CheckoutUnificadoView, CheckoutDireccionView, CheckoutPagoView

urlpatterns = [
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('', views.ver_carrito, name='ver_carrito'),
    path('actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('eliminar/<int:item_id>/', views.eliminar_item, name='eliminar_item'),

    path('checkout/', CheckoutUnificadoView.as_view(), name='checkout_unificado'),
    # Mantén las URLs antiguas para el flujo por pasos si las necesitas


    path('checkout/direccion/', CheckoutDireccionView.as_view(), name='checkout_direccion'),
    path('checkout/pago/', CheckoutPagoView.as_view(), name='checkout_pago'),
    path('checkout/confirmacion/', TemplateView.as_view(template_name='checkout/confirmacion.html'), name='confirmacion_pedido'),
    path('direcciones/agregar/', AgregarDireccionView.as_view(), name='agregar_direccion'),
    path('tarjetas/agregar/', AgregarTarjetaView.as_view(), name='agregar_tarjeta'),
]