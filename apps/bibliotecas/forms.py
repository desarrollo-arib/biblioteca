import re

from django import forms
#from django.contrib.auth.models import User, Group
from .models import  Material, Prestamo, UsuarioPersonalizado, Modulo
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory
from django.forms import modelformset_factory



class UsuarioPersonalizadoCreationForm(UserCreationForm):
    class Meta:
        model = UsuarioPersonalizado
        fields = ('email', 'first_name', 'last_name', 'dni', 'programa_estudio', 'rol')
        labels = {
            'email': 'Correo Electrónico',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'dni': 'DNI',
            'programa_estudio': 'Programa de Estudios',
            'rol': 'Rol',
        }

class UsuarioPersonalizadoChangeForm(UserChangeForm):
    class Meta:
        model = UsuarioPersonalizado
        fields = ('email', 'first_name', 'last_name', 'dni', 'programa_estudio', 'rol', 'is_active')
        labels = {
            'email': 'Correo Electrónico',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'dni': 'DNI',
            'programa_estudio': 'Programa de Estudios',
            'rol': 'Rol',
            'is_active': 'Activo',
        }
    

class FormularioDeInicioSesion(AuthenticationForm):
    username = forms.EmailField(label='Correo Electrónico', max_length=254)

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'titulo', 'autor', 'tipo', 'fecha_publicacion', 'descripcion', 'enlace_archivo','enlace_portada',
            'programa_estudio','isbn', 'editorial', 'num_paginas', 'idioma', 'copias_disponibles', 'disponibilidad'
        ]
        widgets = {
            'fecha_publicacion': forms.DateInput(attrs={'type': 'date'}),
            'disponibilidad': forms.Select(attrs={'class': 'w-full border border-gray-300 p-2 rounded'}),

        }
    
    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        # Inicialmente, los campos específicos no son requeridos
        self.fields['isbn'].required = False
        self.fields['num_paginas'].required = False
        self.fields['editorial'].required = False
        self.fields['idioma'].required = False

        if 'tipo' in self.data:
            tipo = self.data.get('tipo')
        elif self.instance:
            tipo = self.instance.tipo
        else:
            tipo = None

        if tipo == 'Libro':
            # Los campos específicos para libros son requeridos
            self.fields['isbn'].required = True
            self.fields['num_paginas'].required = True
            self.fields['editorial'].required = True
            self.fields['idioma'].required = True
    

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')

        if tipo == 'Libro':
            # Validar que los campos específicos de libros no estén vacíos
            campos_libro = ['isbn', 'editorial', 'num_paginas', 'idioma']
            for campo in campos_libro:
                if not cleaned_data.get(campo):
                    self.add_error(campo, 'Este campo es obligatorio para libros.')
        return cleaned_data
    

    def clean_copias_disponibles(self):
        disponibilidad = self.cleaned_data.get('disponibilidad')
        copias_disponibles = self.cleaned_data.get('copias_disponibles')

        # Si el material es digital, no necesita un número de copias físicas
        if disponibilidad == 'Digital' and copias_disponibles is not None:
            raise forms.ValidationError("No es necesario especificar copias disponibles para material digital.")

        # Si el material es físico o ambos, asegurar que se especifique el número de copias
        if disponibilidad in ['Físico', 'Ambos'] and not copias_disponibles:
            raise forms.ValidationError("Por favor, ingrese el número de copias disponibles para material físico.")

        return copias_disponibles



class PrestamoForm(forms.ModelForm):
    usuario = forms.ModelChoiceField(queryset=UsuarioPersonalizado.objects.all(), label="Usuario")
    material = forms.ModelChoiceField(queryset=Material.objects.all(), label="Material")

    class Meta:
        model = Prestamo
        fields = ['usuario', 'material']

    def clean(self):
        cleaned_data = super().clean()
        usuario = cleaned_data.get('usuario')
        material = cleaned_data.get('material')

        # Validar que el usuario no tenga más de 2 préstamos activos
        prestamos_activos = Prestamo.objects.filter(usuario=usuario, estado='Prestado').count()
        if prestamos_activos >= 2:
            raise forms.ValidationError(f"El usuario {usuario.first_name} ya tiene 2 préstamos activos.")

        return cleaned_data


#class EstudianteForm(forms.ModelForm):
#    class Meta:
#        model = UsuarioPersonalizado
#        fields = ['first_name', 'last_name', 'dni', 'programa_estudio']

class SeleccionarEstudianteForm(forms.Form):
    estudiante = forms.ModelChoiceField(
        queryset=UsuarioPersonalizado.objects.filter(rol='Estudiante'),
        label='Estudiante',
        widget=forms.Select(attrs={'class': 'w-full border border-gray-300 p-2 rounded'})
    )



class ModuloForm(forms.ModelForm):
    estudiante = forms.ModelChoiceField(
        queryset=UsuarioPersonalizado.objects.filter(rol='Estudiante'),
        label='Estudiante',
        widget=forms.Select(attrs={'class': 'w-full border border-gray-300 p-2 rounded'})
    )

    class Meta:
        model = Modulo
        fields = ['estudiante', 'programa_estudio', 'codigo', 'empresa']
        widgets = {
            'programa_estudio': forms.Select(attrs={'class': 'w-full border border-gray-300 p-2 rounded'}),
            'codigo': forms.Select(attrs={'class': 'w-full border border-gray-300 p-2 rounded'}),
            'empresa': forms.TextInput(attrs={'class': 'w-full border border-gray-300 p-2 rounded'}),
        }

    def clean_programa_estudio(self):
        estudiante = self.cleaned_data.get('estudiante')
        programa_estudio = self.cleaned_data.get('programa_estudio')
        
        if estudiante and estudiante.programa_estudio != programa_estudio:
            raise forms.ValidationError("El programa de estudios no coincide con el asignado al estudiante.")
        return programa_estudio

    #def clean_programa_estudio(self):
    #    # Validar que el programa de estudios coincide con el del estudiante seleccionado
    #    estudiante = self.cleaned_data.get('estudiante')
    #    programa_estudio = self.cleaned_data.get('programa_estudio')
    #    if estudiante and estudiante.programa_estudio != programa_estudio:
    #        raise forms.ValidationError("El programa de estudios no coincide con el programa asignado al estudiante.")
    #    return programa_estudio

#class ModuloForm(forms.ModelForm):
#    estudiante = forms.ModelChoiceField(
#        queryset=UsuarioPersonalizado.objects.filter(rol='Estudiante'),
#        label='Estudiante',
#        widget=forms.Select(attrs={'class': 'w-full border border-gray-300 p-2 rounded'})
#    )
#
#    class Meta:
#        model = Modulo
#        fields = ['estudiante','codigo',  'nombre_modulo', 'programa_estudio', 'empresa']
#        widgets = {
#            'codigo': forms.Select(attrs={'class': 'w-full border border-gray-300 p-2 rounded'}),
#            'nombre_modulo': forms.TextInput(attrs={'class': 'w-full border border-gray-300 p-2 rounded'}),
#            'programa_estudio': forms.Select(attrs={'class': 'w-full border border-gray-300 p-2 rounded'}),
#            'empresa': forms.TextInput(attrs={'class': 'w-full border border-gray-300 p-2 rounded'}),
#        }
#
#    
#    def clean(self):
#        cleaned_data = super().clean()
#        estudiante = cleaned_data.get('estudiante')
#        codigo = cleaned_data.get('codigo')
#        programa_estudio = cleaned_data.get('programa_estudio')
#
#        if estudiante and codigo:
#            # Verificar que el programa de estudio coincide
#            if estudiante.programa_estudio != programa_estudio:
#                raise forms.ValidationError("El programa de estudio seleccionado no coincide con el del estudiante.")
#
#            # Verificar si el estudiante ya ha registrado este módulo
#            if Modulo.objects.filter(estudiante=estudiante, codigo=codigo).exists():
#                raise forms.ValidationError(f"El estudiante ya ha registrado el {codigo}.")
#
#            # Obtener el orden del módulo que se intenta registrar
#            orden_modulo = Modulo.MODULO_ORDEN.get(codigo)
#
#            # Obtener los órdenes de los módulos ya registrados por el estudiante
#            modulos_registrados = estudiante.modulos.all()
#            ordenes_registrados = [modulo.orden for modulo in modulos_registrados]
#
#            # Verificar si el estudiante ya completó todos los módulos
#            if len(ordenes_registrados) >= 3:
#                raise forms.ValidationError("El estudiante ya ha completado todos los módulos.")
#
#            # Calcular el siguiente módulo que debe registrar
#            if ordenes_registrados:
#                siguiente_orden = max(ordenes_registrados) + 1
#            else:
#                siguiente_orden = 1
#
#            if orden_modulo != siguiente_orden:
#                modulo_pendiente = [k for k, v in Modulo.MODULO_ORDEN.items() if v == siguiente_orden]
#                modulo_pendiente_nombre = modulo_pendiente[0] if modulo_pendiente else "Módulo desconocido"
#                raise forms.ValidationError(f"Debe registrar el {modulo_pendiente_nombre} antes de registrar este módulo.")
#
#        return cleaned_data



ModuloFormSet = modelformset_factory(
    Modulo,
    form=ModuloForm,
    extra=3,
    can_delete=False,
    min_num=3,
    validate_min=True,
    max_num=3,
    validate_max=True,
)