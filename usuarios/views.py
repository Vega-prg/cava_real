from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import RegistroForm
from django.contrib import messages

class RegistroView(CreateView):
    form_class = RegistroForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('inicio')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
        return response
    
