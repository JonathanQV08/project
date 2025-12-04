from django import forms
from .models import PerfilUsuario


class StyledFormMixin:
    """
    Mixin que agrega estilos TailwindCSS a los campos de formulario.
    Facilita que todos los formularios del sistema mantengan consistencia visual.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Clases CSS definidas para widgets
        text_input_classes = (
            'w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm text-gray-900 '
            'bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 '
            'focus:border-transparent transition-all duration-200 shadow-sm hover:border-gray-400'
        )

        select_classes = (
            'w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm text-gray-900 bg-white '
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent '
            'transition-all duration-200 shadow-sm hover:border-gray-400 cursor-pointer'
        )

        textarea_classes = (
            'w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm text-gray-900 bg-white '
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent '
            'transition-all duration-200 shadow-sm hover:border-gray-400 min-h-[100px] resize-vertical'
        )

        # Asignar clases dependiendo del tipo de widget
        for field_name, field in self.fields.items():
            widget = field.widget
            existing_classes = widget.attrs.get('class', '')

            # Inputs básicos
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.URLInput,
                                   forms.NumberInput, forms.PasswordInput)):
                widget.attrs['class'] = f"{existing_classes} {text_input_classes}".strip()
                widget.attrs.setdefault('placeholder', f'Ingrese {field.label.lower()}')

            # Campos tipo fecha/hora
            elif isinstance(widget, (forms.DateInput, forms.TimeInput, forms.DateTimeInput)):
                widget.attrs['class'] = f"{existing_classes} {text_input_classes}".strip()

            # Selects
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = f"{existing_classes} {select_classes}".strip()

            # Textareas
            elif isinstance(widget, forms.Textarea):
                widget.attrs['class'] = f"{existing_classes} {textarea_classes}".strip()
                widget.attrs.setdefault('rows', 4)
                widget.attrs.setdefault('placeholder', f'Ingrese {field.label.lower()}')


class PerfilUsuarioForm(StyledFormMixin, forms.ModelForm):
    """
    Formulario para crear o actualizar perfiles de usuario.
    Aplica estilos mediante StyledFormMixin.
    """

    class Meta:
        model = PerfilUsuario
        fields = ['user', 'rol', 'trabajador']
        labels = {
            'user': 'Usuario',
            'rol': 'Rol',
            'trabajador': 'Trabajador',
        }

    def __init__(self, *args, **kwargs):
        """
        Al editar un perfil existente, el usuario no debe cambiarse.
        Solo los administradores asignan el usuario al crear el perfil.
        """
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            # Bloquear edición del campo user
            self.fields['user'].disabled = True
