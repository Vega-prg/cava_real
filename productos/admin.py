from django.contrib import admin
from .models import Categoria, Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'disponible', 'stock', 'fecha_creacion', 'graduacion_alcoholica')
    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}

admin.site.register(Categoria)