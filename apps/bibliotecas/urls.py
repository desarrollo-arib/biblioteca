from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from .views import UsuarioListView, MaterialListView, MaterialCreateView, MaterialUpdateView, MaterialDeleteView,BibliotecaView, PrestamoListView, MisPrestamosView


urlpatterns = [
    #path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    #path('login/', views.login_view, name='login'),
    #path('login/', IniciarSesion.as_view(), name='login'),
    path('login/', views.login_usuario, name='login'),
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('no-autorizado/', views.no_autorizado, name='no_autorizado'),
    #path('agregar-material/', views.agregar_material, name='agregar_material'),
    # rutas material
    path('materiales/', MaterialListView.as_view(), name='material_list'),
    path('materiales/nuevo/', MaterialCreateView.as_view(), name='material_create'),
    path('materiales/editar/<int:pk>/', MaterialUpdateView.as_view(), name='material_update'),
    path('materiales/eliminar/<int:pk>/', MaterialDeleteView.as_view(), name='material_delete'),
    #rutas efsrt
    #path('experiencias/', ExperienciaFormativaListView.as_view(), name='experiencia_formativa_list'),
    #path('experiencias/nueva/', ExperienciaFormativaCreateView.as_view(), name='experiencia_formativa_create'),
    #ruta biblioteca
    path('biblioteca/', BibliotecaView.as_view(), name='biblioteca_virtual'),
    #rutas prestamos
    path('bibliotecario/prestamos/crear/', views.crear_prestamo, name='crear_prestamo' ),
    path('bibliotecario/prestamos/', views.listar_prestamos_activos, name='listar_prestamos'),
    path('bibliotecario/prestamos/devolver/<int:pk>/', views.registrar_devolucion, name='registrar_devolucion'),
    path('mis-prestamos/', MisPrestamosView.as_view(), name='mis_prestamos'),
    #dashboard
    path('dashboard/admin/', views.dashboard, name='dashboard_admin'),
    path('dashboard/bibliotecario/', views.dashboard_bibliotecario, name='dashboard_bibliotecario'),
    #usuarios
    path('usuarios/', UsuarioListView.as_view(), name='listar_usuarios'),
    path('usuarios/registrar', views.registrar_usuario, name='registrar_usuario'),
    path('usuarios/<int:usuario_id>/restablecer_contraseña/', views.restablecer_contraseña, name='restablecer_contraseña'),
    path('modulos/registrar/', views.registrar_modulo, name='registrar_modulo'),
    path('estudiantes/<int:estudiante_id>/', views.detalle_estudiante, name='detalle_estudiante'),
    path('estudiantes/<int:estudiante_id>/constancia/pdf/', views.generar_constancia_pdf, name='generar_constancia_pdf'),
    path('estudiantes/', views.listar_estudiantes, name='listar_estudiantes'),

]