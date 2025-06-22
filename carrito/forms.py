from django import forms
from .models import DireccionEnvio, MetodoPago


class SeleccionarDireccionForm(forms.Form):
    direccion = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        empty_label=None,
        label="Selecciona una dirección"
    )

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['direccion'].queryset = DireccionEnvio.objects.filter(usuario=usuario)
        self.fields['direccion'].initial = DireccionEnvio.objects.filter(usuario=usuario, default=True).first()

class SeleccionarMetodoPagoForm(forms.Form):
    metodo_pago = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        empty_label=None,
        label="Selecciona un método de pago"
    )

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['metodo_pago'].queryset = MetodoPago.objects.filter(usuario=usuario, activo=True)
        self.fields['metodo_pago'].initial = MetodoPago.objects.filter(usuario=usuario, default=True).first()

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['metodo_pago'].queryset = MetodoPago.objects.filter(usuario=usuario, activo=True)
        self.fields['metodo_pago'].initial = MetodoPago.objects.filter(usuario=usuario, default=True).first()

class MetodoPagoForm(forms.Form):
    OPCIONES_PAGO = [
        ('EFECTIVO', 'Pago en efectivo al recibir'),
        ('TARJETA', 'Tarjeta de crédito/débito'),
    ]
    
    metodo = forms.ChoiceField(
        choices=OPCIONES_PAGO,
        widget=forms.RadioSelect,
        initial='TARJETA'
    )
    
    # Campos condicionales para tarjeta
    numero_tarjeta = forms.CharField(required=False, max_length=16, label="Número de tarjeta")
    nombre_titular = forms.CharField(required=False, max_length=100, label="Nombre en la tarjeta")
    fecha_expiracion = forms.CharField(required=False, max_length=5, label="MM/AA")
    cvv = forms.CharField(required=False, max_length=4, label="CVV")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('metodo') == 'TARJETA':
            if not all([
                cleaned_data.get('numero_tarjeta'),
                cleaned_data.get('nombre_titular'),
                cleaned_data.get('fecha_expiracion'),
                cleaned_data.get('cvv')
            ]):
                raise forms.ValidationError("Todos los campos de tarjeta son obligatorios.")
        return cleaned_data
    

class DireccionEnvioForm(forms.ModelForm):
    class Meta:
        model = DireccionEnvio
        fields = ['direccion', 'ciudad', 'provincia', 'codigo_postal', 'telefono', 'instrucciones']
        widgets = {
            'instrucciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})