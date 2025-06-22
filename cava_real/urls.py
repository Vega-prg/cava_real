from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', TemplateView.as_view(template_name='inicio.html'), name='inicio'),  # Página de inicio
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),  # Incluye las URLs de la app usuarios
    path('productos/', include('productos.urls')),
    path('carrito/', include('carrito.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Para servir imágenes
   
