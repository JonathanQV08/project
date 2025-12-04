# core/forms.py
from django import forms
from .models import CalendarioLaboral, Puesto, TipoNombramiento, TipoIncidencia, UnidadAdministrativa

class StyledFormMixin:
    """Mixin para aplicar estilos automáticamente a los formularios"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        text_input_classes = 'w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 shadow-sm hover:border-gray-400'
        
        select_classes = 'w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 shadow-sm hover:border-gray-400 cursor-pointer'
        
        textarea_classes = 'w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 shadow-sm hover:border-gray-400 min-h-[100px] resize-vertical'
        
        for field_name, field in self.fields.items():
            widget = field.widget
            existing_classes = widget.attrs.get('class', '')
            
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.URLInput, 
                                 forms.NumberInput, forms.PasswordInput)):
                widget.attrs['class'] = f"{existing_classes} {text_input_classes}".strip()
                widget.attrs['placeholder'] = widget.attrs.get('placeholder', f'Ingrese {field.label.lower()}')
            
            elif isinstance(widget, (forms.DateInput, forms.TimeInput, forms.DateTimeInput)):
                widget.attrs['class'] = f"{existing_classes} {text_input_classes}".strip()
            
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = f"{existing_classes} {select_classes}".strip()
            
            elif isinstance(widget, forms.Textarea):
                widget.attrs['class'] = f"{existing_classes} {textarea_classes}".strip()
                widget.attrs['placeholder'] = widget.attrs.get('placeholder', f'Ingrese {field.label.lower()}')
                widget.attrs['rows'] = widget.attrs.get('rows', 4)

class ColoredFormMixin(StyledFormMixin):
    color_scheme = 'indigo'  # Color por defecto
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        color = self.color_scheme
        
        for field_name, field in self.fields.items():
            widget = field.widget
            current_classes = widget.attrs.get('class', '')
            
            # Reemplazar color de focus
            new_classes = current_classes.replace('ring-indigo-500', f'ring-{color}-500')
            widget.attrs['class'] = new_classes

class UnidadAdministrativaForm(ColoredFormMixin, forms.ModelForm):
    class Meta:
        color_scheme = 'purple'
        model = UnidadAdministrativa
        fields = ['nombre', 'descripcion', 'unidad_padre']
        labels = {
            'nombre': 'Nombre de la Unidad',
            'descripcion': 'Descripción breve',
            'unidad_padre': 'Unidad Superior (Jerarquía)'
        }
        help_texts = {
            'unidad_padre': 'Seleccione solo si esta unidad depende de otra.'
        }                

class PuestoForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        color_scheme = 'blue'
        model = Puesto
        fields = ['nombre_puesto', 'nivel']
        labels = {
            'nombre_puesto': 'Nombre del Puesto',
            'nivel': 'Nivel Jerárquico'
        }
        help_texts = {
            'nombre_puesto': 'Ejemplo: Director, Maestro, Intendente',
            'nivel': 'Seleccione el nivel jerárquico del puesto'
        }        
class TipoNombramientoForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        color_scheme = 'emerald'
        model = TipoNombramiento
        fields = ['descripcion']
        labels = {
            'descripcion': 'Tipo de Nombramiento'
        }
        help_texts = {
            'descripcion': 'Ejemplo: Base, Confianza, Interino'
        }
        
class TipoIncidenciaForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        color_scheme = 'amber'
        model = TipoIncidencia
        fields = ['descripcion']
        labels = {
            'descripcion': 'Tipo de Incidencia'
        }
        help_texts = {
            'descripcion': 'Ejemplo: Incapacidad médica, Permiso con goce'
        }        

class CalendarioLaboralForm(ColoredFormMixin, forms.ModelForm):
    class Meta:
        color_scheme = 'rose'
        model = CalendarioLaboral
        fields = ['fecha', 'es_inhabil', 'descripcion']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'fecha': 'Fecha del Evento',
            'es_inhabil': '¿Es día inhábil?',
            'descripcion': 'Motivo o Festividad'
        }        