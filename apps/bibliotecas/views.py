import uuid


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User


from datetime import timedelta

from .forms import  MaterialForm, ModuloFormSet, SeleccionarEstudianteForm, ModuloForm
#PrestamoForm
#RegistroForm,
from .decorators import rol_requerido
from .models import Material,  Prestamo, StockLibro, UsuarioPersonalizado, Constancia, Modulo
from .forms import UsuarioPersonalizadoCreationForm, FormularioDeInicioSesion, PrestamoForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.crypto import get_random_string
from django.contrib.auth.views import LoginView

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Count
from django.db.models.functions import ExtractYear
from django.core.exceptions import ValidationError




def login_usuario(request):
    if request.user.is_authenticated:
        return redirect('biblioteca_virtual')  # Redirige a la página principal si ya está autenticado

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'biblioteca_virtual')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'login_usuario.html')


#Vista para registrar usuario
@login_required
@permission_required('gestion.add_usuariopersonalizado', raise_exception=True)
def registrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioPersonalizadoCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            # Puedes enviar un correo electrónico al usuario con la contraseña o instrucciones
            return redirect('listar_usuarios')
    else:
        form = UsuarioPersonalizadoCreationForm()
    return render(request, 'registro/registro.html', {'form': form})



class UsuarioListView(ListView):
    model = UsuarioPersonalizado
    template_name = 'registro/listar_usuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 10  # Número de usuarios por página (opcional)

#vista para restablecer contraseña
@login_required
@permission_required('gestion.change_usuariopersonalizado', raise_exception=True)
def restablecer_contraseña(request, usuario_id):
    usuario = UsuarioPersonalizado.objects.get(pk=usuario_id)
    nueva_contraseña = get_random_string(length=8)  # Genera una contraseña aleatoria
    usuario.set_password(nueva_contraseña)
    usuario.save()
    # Puedes enviar un correo electrónico al usuario con la nueva contraseña
    messages.success(request, f'La contraseña de {usuario.email} ha sido restablecida.')
    return redirect('listar_usuarios')

#@login_required
#@user_passes_test(lambda u: hasattr(u, 'perfil') and u.perfil.rol == 'Administrador', login_url='no_autorizado')
#def registro(request):
#    if request.method == 'POST':
#        form = RegistroForm(request.POST)
#        if form.is_valid():
#            form.save()
#            return redirect('login')
#    else:
#        form = RegistroForm()
#    return render(request, 'registro.html', {'form': form})

def no_autorizado(request):
    return render(request, 'no_autorizado.html')

@login_required
#@user_passes_test(lambda u: hasattr(u, 'perfil') and u.perfil.rol == 'Administrador', login_url='no_autorizado')
def dashboard_admin(request):
    total_materiales = Material.objects.count()
    # Otros cálculos
    context = {
        'total_materiales': total_materiales,
        # Más datos
    }
    return render(request, 'dashboard_admin.html', context)



@login_required
@user_passes_test(lambda u: hasattr(u, 'perfil') and u.perfil.rol == 'Bibliotecario', login_url='no_autorizado')
def dashboard_bibliotecario(request):
    return render(request, 'dashboard_bibliotecario.html')



class EsAdministradorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.rol == 'Administrador'

class MaterialListView(LoginRequiredMixin, EsAdministradorMixin, ListView):
    model = Material
    template_name = 'material/material_list.html'

class MaterialCreateView(LoginRequiredMixin, EsAdministradorMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'material/material_form.html'
    success_url = reverse_lazy('material_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Agregar'
        return context

    def form_valid(self, form):
        # Verificar la disponibilidad y otras validaciones personalizadas aquí
        material = form.save(commit=False)
        if material.disponibilidad == 'Digital':
            material.copias_disponibles = None  # No es necesario especificar copias para digital
        elif material.disponibilidad == 'Físico' and material.copias_disponibles is None:
            messages.error(self.request, "Por favor, ingrese el número de copias disponibles para material físico.")
            return self.form_invalid(form)
        messages.success(self.request, "Material registrado exitosamente.")
        return super().form_valid(form)

class MaterialUpdateView(LoginRequiredMixin, EsAdministradorMixin, UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = 'material/material_form.html'
    success_url = reverse_lazy('material_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Agregar' if isinstance(self, MaterialCreateView) else 'Editar'
        return context

class MaterialDeleteView(LoginRequiredMixin, EsAdministradorMixin, DeleteView):
    model = Material
    template_name = 'material/material_confirm_delete.html'
    success_url = reverse_lazy('material_list')


class BibliotecaView(LoginRequiredMixin, ListView):
    model = Material
    template_name = 'biblioteca_virtual.html'
    context_object_name = 'materiales'
    #paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        programa_estudio = self.request.GET.get('programa_estudio')
        fecha_publicacion =self.request.GET.get('fecha_publicacion')
        tipo = self.request.GET.get('tipo')
        if query:
            queryset = queryset.filter(
                Q(titulo__icontains=query) |
                Q(autor__icontains=query) |
                Q(tipo__icontains=query) |
                Q(programa_estudio__icontains=query)
            )
        if programa_estudio:
            queryset = queryset.filter(programa_estudio=programa_estudio)

        if fecha_publicacion:
            queryset = queryset.annotate(año=ExtractYear('fecha_publicacion')).filter(año=fecha_publicacion)


        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener las opciones para los filtros
        context['programas'] = Material.objects.values_list('programa_estudio', flat=True).distinct()
        context['años_publicacion'] = Material.objects.annotate(año=ExtractYear('fecha_publicacion')).values_list('año', flat=True).distinct().order_by('-año')
        context['tipos'] = Material.objects.values_list('tipo', flat=True).distinct()

        # Agregar los valores actuales de los filtros al contexto para mantenerlos en el formulario
        context['q'] = self.request.GET.get('q', '')
        context['programa_estudio_actual'] = self.request.GET.get('programa_estudio', '')
        context['fecha_publicacion_actual'] = self.request.GET.get('fecha_publicacion', '')
        context['tipo_actual'] = self.request.GET.get('tipo', '')

        return context
    
@transaction.atomic
@login_required
def crear_prestamo(request):
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            prestamo = form.save(commit=False)
            # Establecer la fecha de devolución (2 días después)
            prestamo.fecha_devolucion = timezone.now() + timedelta(days=2)
            prestamo.save()
            messages.success(request, f"Préstamo registrado para {prestamo.usuario.first_name}.")
            return redirect('listar_prestamos')
        else:
            messages.error(request, "Error al registrar el préstamo. Por favor, verifica los datos.")
    else:
        form = PrestamoForm()
    return render(request, 'prestamo/crear_prestamo.html', {'form': form})

class PrestamoListView(LoginRequiredMixin, ListView):
    model = Prestamo
    template_name = 'prestamo/prestamo_list.html'



@transaction.atomic
@login_required
#@user_passes_test(lambda u: hasattr(u, 'perfil') and u.perfil.rol == 'Bibliotecario', login_url='no_autorizado')
def registrar_devolucion(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    if request.method == 'POST':
        prestamo.estado = 'Devuelto'
        prestamo.fecha_devolucion_real = timezone.now().date()
        prestamo.save()
        messages.success(request, f"Devolución registrada para {prestamo.usuario.first_name}.")
        return redirect('listar_prestamos')
    return render(request, 'prestamo/registrar_devolucion.html', {'prestamo': prestamo})


class MisPrestamosView(LoginRequiredMixin, ListView):
    model = Prestamo
    template_name = 'prestamo/mis_prestamos.html'
    context_object_name = 'prestamos'

    def get_queryset(self):
        return Prestamo.objects.filter(usuario=self.request.user, estado='Prestado')


def listar_prestamos_activos(request):
    prestamos_activos = Prestamo.objects.filter(estado='Prestado')
    return render(request, 'prestamo/listar_prestamos_activos.html', {'prestamos': prestamos_activos})

#def registrar_modulo(request):
#    if request.method == 'POST':
#        form = ModuloForm(request.POST)
#        if form.is_valid():
#            estudiante = form.cleaned_data['estudiante']
#            if estudiante.modulos.count() >= 3:
#                messages.error(request, 'El estudiante ya tiene tres módulos registrados.')
#                return redirect('detalle_estudiante', estudiante_id=estudiante.id)
#            modulo = form.save()
#            estudiante = modulo.estudiante
#            total_modulos = estudiante.modulos.count()
#            if total_modulos == 3:
#                # Generar constancia si aún no existe
#                if not hasattr(estudiante, 'constancia'):
#                    Constancia.objects.create(
#                        estudiante=estudiante,
#                        codigo_constancia=generar_codigo_constancia()
#                    )
#                    messages.success(request, f"Se ha generado la constancia para el estudiante {estudiante.first_name} {estudiante.last_name}.")
#                else:
#                    messages.info(request, 'El estudiante ya tiene una constancia generada.')
#            elif total_modulos > 3:
#                messages.warning(request, 'El estudiante ya tiene más de tres módulos registrados.')
#            else:
#                messages.success(request, 'Módulo registrado exitosamente.')
#            return redirect('detalle_estudiante', estudiante_id=estudiante.id)
#    else:
#        form = ModuloForm()
#    return render(request, 'registrar_modulo.html', {'form': form})
#def registrar_modulo(request):
#    if request.method == 'POST':
#        form = ModuloForm(request.POST)
#        if form.is_valid():
#            modulo = form.save()
#            estudiante = modulo.estudiante
#            total_modulos = estudiante.modulos.count()
#            if total_modulos == 3:
#                # Generar constancia si aún no existe
#                if not hasattr(estudiante, 'constancia'):
#                    Constancia.objects.create(
#                        estudiante=estudiante,
#                        codigo_constancia=generar_codigo_constancia()
#                    )
#                    messages.success(request, f"Se ha generado la constancia para el estudiante {estudiante.get_full_name()}.")
#                else:
#                    messages.info(request, 'El estudiante ya tiene una constancia generada.')
#            else:
#                messages.success(request, 'Módulo registrado exitosamente.')
#            return redirect('detalle_estudiante', estudiante_id=estudiante.id)
#        else:
#            # Si el formulario no es válido, se mostrarán los errores en la plantilla
#            pass
#    else:
#        form = ModuloForm()
#    return render(request, 'registrar_modulo.html', {'form': form})


def registrar_modulo(request):
    if request.method == 'POST':
        form = ModuloForm(request.POST)
        if form.is_valid():
            modulo = form.save(commit=False)
            
            # Validar que el módulo es el siguiente en el orden
            estudiante = modulo.estudiante
            programa_estudio = modulo.programa_estudio
            modulos_completados = estudiante.modulos.filter(programa_estudio=programa_estudio).count()
            siguiente_modulo = f'Modulo {modulos_completados + 1}'
            
            if modulo.codigo != siguiente_modulo:
                messages.error(request, f"Debe registrar {siguiente_modulo} antes de registrar {modulo.codigo}.")
                return redirect('registrar_modulo')

            # Guardar el módulo
            modulo.save()

            # Verificar si el estudiante completó todos los módulos para generar la constancia
            if estudiante.modulos.filter(programa_estudio=programa_estudio).count() == 3:
                Constancia.objects.get_or_create(
                    estudiante=estudiante,
                    defaults={'codigo_constancia': f"CONST-{estudiante.dni}-{timezone.now().year}"}
                )
                messages.success(request, f"Constancia generada para el estudiante {estudiante.first_name} {estudiante.last_name}.")
            else:
                messages.success(request, "Módulo registrado exitosamente.")
            return redirect('detalle_estudiante', estudiante_id=estudiante.id)
    else:
        form = ModuloForm()
    return render(request, 'registrar_modulo.html', {'form': form})


def generar_codigo_constancia():
    return str(uuid.uuid4()).split('-')[0].upper()


def detalle_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(UsuarioPersonalizado, id=estudiante_id, rol='Estudiante')
    modulos = estudiante.modulos.all()
    constancia = getattr(estudiante, 'constancia', None)
    return render(request, 'detalle_estudiante.html', {
        'estudiante': estudiante,
        'modulos': modulos,
        'constancia': constancia
    })

  

def generar_constancia_pdf(request, estudiante_id):
    estudiante = get_object_or_404(UsuarioPersonalizado, id=estudiante_id, rol='Estudiante')
    constancia = getattr(estudiante, 'constancia', None)
    if not constancia:
        messages.error(request, 'El egresado aún no tiene una constancia generada.')
        return redirect('detalle_estudiante', estudiante_id=estudiante.id)

    modulos = estudiante.modulos.all()
    html_string = render_to_string('detalle_constancia.html', {
        'estudiante': estudiante,
        'constancia': constancia,
        'modulos': modulos
    })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Constancia_{estudiante.dni}.pdf"'
    HTML(string=html_string).write_pdf(response)
    return response

def listar_estudiantes(request):
    estudiantes = UsuarioPersonalizado.objects.filter(rol='Estudiante')
    return render(request, 'listar_estudiantes.html', {'estudiantes': estudiantes})


#def dashboard_admin(request):
#    usuarios__por_rol = UsuarioPersonalizado.objects.values('rol').annotate(total=Count('id'))
#    # Contar préstamos por tipo de material
#    prestamos_por_tipo = Prestamo.objects.values('material__tipo').annotate(total=Count('id'))
#
#    # Convertir a diccionario
#    prestamos_por_tipo_dict = {item['material__tipo']: item['total'] for item in prestamos_por_tipo}
#    # Títulos más prestados
#    titulos_mas_prestados = Prestamo.objects.values('material__titulo').annotate(total=Count('id')).order_by('-total')[:5]  # Top 5
#    empresas_efsrt = Modulo.objects.values('empresa').annotate(total=Count('id')).order_by('-total')[:5]  # Top 5
#    # Materiales por programa de estudio
#    materiales_por_programa = Material.objects.values('programa_estudio').annotate(total=Count('id'))
#
#    # Préstamos activos y retrasados
#    prestamos_activos = Prestamo.objects.filter(estado='Activo').count()
#    prestamos_retrasados = Prestamo.objects.filter(estado='Retrasado').count()
#
#    context = {
#        'usuarios_por_rol': usuarios_por_rol_dict,
#        'prestamos_por_tipo': prestamos_por_tipo_dict,
#        'titulos_mas_prestados': titulos_mas_prestados,
#        'empresas_efsrt': empresas_efsrt,
#        'materiales_por_programa': materiales_por_programa,
#        'prestamos_activos': prestamos_activos,
#        'prestamos_retrasados': prestamos_retrasados,
#    }
#
#    return render(request, 'dashboard_admin.html', context)


def dashboard(request):
    # Reporte de usuarios por rol
    usuarios_por_rol = UsuarioPersonalizado.objects.values('rol').annotate(total=Count('id'))

    # Reporte de préstamos por tipo de material
    prestamos_por_tipo = Prestamo.objects.values('material__tipo').annotate(total=Count('id'))

    # Título más buscado (supongamos que tenemos un modelo de búsquedas)
    # Si no lo tienes, podemos usar los materiales más prestados
    materiales_mas_prestados = Prestamo.objects.values('material__titulo').annotate(total=Count('id')).order_by('-total')[:5]

    # Empresa con más EFSRT
    empresas_efsrt = Modulo.objects.values('empresa').annotate(total=Count('id')).order_by('-total')[:5]

    # Otros reportes que podríamos incluir
    # - Número total de materiales por tipo
    materiales_por_tipo = Material.objects.values('tipo').annotate(total=Count('id'))

    context = {
        'usuarios_por_rol': usuarios_por_rol,
        'prestamos_por_tipo': prestamos_por_tipo,
        'materiales_mas_prestados': materiales_mas_prestados,
        'empresas_efsrt': empresas_efsrt,
        'materiales_por_tipo': materiales_por_tipo,
    }
    return render(request, 'dashboard.html', context)
