# gestion/management/commands/crear_grupos.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.bibliotecas.models import Material

class Command(BaseCommand):
    help = 'Crea los grupos y permisos predeterminados'

    def handle(self, *args, **kwargs):
        # Crear grupos
        administrador, created = Group.objects.get_or_create(name='Administrador')
        bibliotecario, created = Group.objects.get_or_create(name='Bibliotecario')
        estudiante, created = Group.objects.get_or_create(name='Estudiante')
        docente, created = Group.objects.get_or_create(name='Docente')

        # Definir permisos (ejemplo)
        content_type = ContentType.objects.get_for_model(Material)

        permiso_agregar_material = Permission.objects.get(codename='add_material', content_type=content_type)
        permiso_cambiar_material = Permission.objects.get(codename='change_material', content_type=content_type)
        permiso_ver_material = Permission.objects.get(codename='view_material', content_type=content_type)
        permiso_eliminar_material = Permission.objects.get(codename='delete_material', content_type=content_type)

        # Asignar permisos a grupos
        administrador.permissions.add(permiso_agregar_material, permiso_cambiar_material, permiso_ver_material, permiso_eliminar_material)
        bibliotecario.permissions.add(permiso_ver_material)
        estudiante.permissions.add(permiso_ver_material)
        docente.permissions.add(permiso_ver_material)

        self.stdout.write('Grupos y permisos creados exitosamente.')