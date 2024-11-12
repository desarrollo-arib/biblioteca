from django.db import models
#from django.contrib.auth.models import User
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class UsuarioPersonalizadoManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, dni, programa_estudio, rol, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico.')
        if not dni:
            raise ValueError('El usuario debe tener un DNI.')

        email = self.normalize_email(email)
        usuario = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            programa_estudio=programa_estudio,
            rol=rol,
            **extra_fields
        )
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, first_name, last_name, dni, programa_estudio, rol, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if rol != 'Administrador':
            raise ValueError('El superusuario debe tener el rol de Administrador.')

        return self.create_user(email, first_name, last_name, dni, programa_estudio, rol, password, **extra_fields)

class UsuarioPersonalizado(AbstractBaseUser, PermissionsMixin):
    PROGRAMA_ESTUDIO_CHOICES = [
        ('Contabilidad', 'Contabilidad'),
        ('Construcción Civil', 'Construcción Civil'),
        ('Explotación Minera', 'Explotación Minera'),
        ('Empleabilidad', 'Empleabilidad'),
    ]

    ROLES_CHOICES = [
        ('Estudiante', 'Estudiante'),
        ('Docente', 'Docente'),
        ('Bibliotecario', 'Bibliotecario'),
        ('Administrador', 'Administrador'),
    ]

    email = models.EmailField('Correo Electrónico', unique=True)
    first_name = models.CharField('Nombres', max_length=30)
    last_name = models.CharField('Apellidos', max_length=30)
    dni = models.CharField('DNI', max_length=20, unique=True)
    programa_estudio = models.CharField('Programa de Estudios', max_length=50, choices=PROGRAMA_ESTUDIO_CHOICES)
    rol = models.CharField('Rol', max_length=20, choices=ROLES_CHOICES)
    is_active = models.BooleanField('Activo', default=True)
    is_staff = models.BooleanField('Es Staff', default=False)
    date_joined = models.DateTimeField('Fecha de Registro', default=timezone.now)
    objects = UsuarioPersonalizadoManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'dni', 'programa_estudio', 'rol']

    def __str__(self):
        return f"{self.dni} - {self.first_name} {self.last_name} ({self.email})"


class Material(models.Model):
    DISPONIBILIDAD_CHOICES = [
        ('Físico', 'Físico'),
        ('Digital', 'Digital'),
        ('Ambos', 'Ambos')
    ]
    TITULO_TIPO_CHOICES = [
        ('Libro', 'Libro'),
        ('Tesis', 'Tesis'),
        ('Artículo', 'Artículo'),
        ('Efsrt', 'Efsrt'),
        # Otros tipos...
    ]

    PROGRAMA_ESTUDIO_CHOICES = [
        ('Contabilidad', 'Contabilidad'),
        ('Construcción Civil', 'Construcción Civil'),
        ('Explotación Minera', 'Explotación Minera'),
        ('Transversal', 'Transversal'),
        # Agrega más programas si es necesario
    ]

    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TITULO_TIPO_CHOICES)
    fecha_publicacion = models.DateField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    disponibilidad = models.CharField(max_length=10, choices=DISPONIBILIDAD_CHOICES, default='Físico')

    # Enlaces de Google Drive
    enlace_portada = models.CharField(max_length=100, null=True, blank=True)
    enlace_archivo = models.CharField(max_length=100, null=True, blank=True)
    
    # Campos específicos para libros
    isbn = models.CharField(max_length=20, null=True, blank=True)
    editorial = models.CharField(max_length=255, null=True, blank=True)
    num_paginas = models.PositiveIntegerField(null=True, blank=True)
    idioma = models.CharField(max_length=50, null=True, blank=True)
    programa_estudio = models.CharField(max_length=50, choices=PROGRAMA_ESTUDIO_CHOICES)
    copias_disponibles = models.PositiveIntegerField(default=1)

    #Método para verificar disponibilidad
    def esta_disponible(self):
        return self.copias_disponibles > 0

    #def get_portada_url(self):
    #    if self.enlace_portada:
    #        drive_id = self.extract_drive_id(self.enlace_portada)
    #        return f"https://drive.google.com/uc?export=view&id={drive_id}"
    #    return ""
    def get_portada_url(self):
        if self.enlace_portada:
            drive_id = self.extract_drive_id(self.enlace_portada)
            # Cambiamos a un enlace de visualización de Google Drive en miniatura para mejor compatibilidad
            return f"https://drive.google.com/thumbnail?id={drive_id}"
        return ""

    def get_previsualizacion_url(self):
        if self.enlace_archivo:
            drive_id = self.extract_drive_id(self.enlace_archivo)
            return f"https://drive.google.com/file/d/{drive_id}/view"
        return ""

    def get_archivo_url(self):
        if self.enlace_archivo:
            drive_id = self.extract_drive_id(self.enlace_archivo)
            return f"https://drive.google.com/uc?export=download&id={drive_id}"
        return ""

    def extract_drive_id(self, url):
        import re
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        return None

    def copias_texto(self):
        # Mostrar "Ilimitado" si el libro está en digital, o el número de copias si es físico
        if self.disponibilidad in ['Digital', 'Ambos']:
            return "Ilimitado"
        return str(self.copias_disponibles)


class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('Prestado', 'Prestado'),
        ('Devuelto', 'Devuelto'),
        ('Retrasado', 'Retrasado'),
    ]
    usuario = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateTimeField()
    fecha_devolucion_real = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Prestado')

    def clean(self):
        if self.estado == 'Prestado':
            # Validar que el usuario no tenga más de 2 préstamos activos
            prestamos_activos = Prestamo.objects.filter(usuario=self.usuario, estado='Prestado').exclude(pk=self.pk).count()
            if prestamos_activos >= 2:
                raise ValidationError("El usuario no puede tener más de 2 préstamos activos.")

            # Validar disponibilidad del material
            if self.material.copias_disponibles <= 0:
                raise ValidationError(f"No hay copias disponibles de '{self.material.titulo}'.")

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        previous_estado = None
        if not is_new:
            # Obtener el estado anterior
            previous = Prestamo.objects.get(pk=self.pk)
            previous_estado = previous.estado

        super().save(*args, **kwargs)

        # Disminuir o aumentar copias según el estado
        if self.estado == 'Prestado' and (is_new or previous_estado != 'Prestado'):
            # Disminuir copias disponibles
            self.material.copias_disponibles -= 1
            self.material.save()
        elif self.estado == 'Devuelto' and previous_estado == 'Prestado':
            # Aumentar copias disponibles
            self.material.copias_disponibles += 1
            self.material.save()

    @property
    def esta_retrasado(self):
        if self.estado == 'Prestado' and self.fecha_devolucion < timezone.now():
            return True
        return False
    

class StockLibro(models.Model):
    libro = models.OneToOneField(Material, on_delete=models.CASCADE)
    cantidad_total = models.PositiveIntegerField()
    cantidad_disponible = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.libro.titulo} - Disponibles: {self.cantidad_disponible}"



class Modulo(models.Model):
    MODULO_CHOICES = [
        ('Modulo I', 'Modulo I'),
        ('Modulo II', 'Modulo II'),
        ('Modulo III', 'Modulo III'),
    ]
    PROGRAMA_ESTUDIO_CHOICES = UsuarioPersonalizado.PROGRAMA_ESTUDIO_CHOICES
    MODULOS_POR_PROGRAMA = {
        'Explotación Minera': {
            'Modulo I': 'Proceso de explotación minera',
            'Modulo II': 'Perforación y Voladura',
            'Modulo III': 'Explotación de Minerales y Supervisión y Control Minero',
        },
        'Contabilidad': {
            'Modulo I': 'Procesos Contables',
            'Modulo II': 'Contabilidad Pública y Privada',
            'Modulo III': 'Análisis Financiero',
        },
        'Construcción Civil': {
            'Modulo I': 'Topografía',
            'Modulo II': 'Análisis del Expediente Técnico',
            'Modulo III': 'Ejecución de Obras Civiles',
        }
    }

    estudiante = models.ForeignKey(
        UsuarioPersonalizado,
        on_delete=models.CASCADE,
        related_name='modulos',
        limit_choices_to={'rol': 'Estudiante'}
    )
    codigo = models.CharField('Código del Módulo', max_length=50, choices=MODULO_CHOICES)
    nombre_modulo = models.CharField('Nombre del Módulo', max_length=100, blank=True)
    programa_estudio = models.CharField(
        'Programa de Estudios',
        max_length=50,
        choices=PROGRAMA_ESTUDIO_CHOICES
    )
    empresa = models.CharField('Empresa donde realizó la práctica', max_length=255)
    fecha_ingreso = models.DateField('Fecha de Ingreso', auto_now_add=True)

    class Meta:
        unique_together = ('estudiante', 'codigo')

    def __str__(self):
        return f"{self.nombre_modulo} - {self.estudiante.first_name} {self.estudiante.last_name}" if self.estudiante_id else self.nombre_modulo
    
    
    #def save(self, *args, **kwargs):
    #    # Asignar automáticamente el nombre del módulo basado en el programa
    #    if not self.nombre_modulo and self.programa_estudio in self.MODULOS_POR_PROGRAMA:
    #        self.nombre_modulo = self.MODULOS_POR_PROGRAMA[self.programa_estudio].get(self.codigo, "")
    #    super().save(*args, **kwargs)

    #def clean(self):
    #    # Verificar el orden de los módulos completados
    #    modulos_completados = self.estudiante.modulos.filter(programa_estudio=self.programa_estudio).count()
    #    siguiente_modulo = list(self.MODULO_ORDEN.keys())[modulos_completados]
#
    #    if self.codigo != siguiente_modulo:
    #        raise ValidationError(f"Debe registrar {siguiente_modulo} antes de registrar {self.codigo}.")
#
    #    # Asignar el nombre del módulo en función del programa de estudios
    #    if not self.nombre_modulo and self.programa_estudio in self.MODULOS_POR_PROGRAMA:
    #        self.nombre_modulo = self.MODULOS_POR_PROGRAMA[self.programa_estudio].get(self.codigo, "")

    #def save(self, *args, **kwargs):
    #    self.clean()  # Ejecutar la validación antes de guardar
    #    super().save(*args, **kwargs)
#
    #    # Generar constancia si se han completado los módulos en orden
    #    modulos_ordenados = self.estudiante.modulos.filter(programa_estudio=self.programa_estudio).order_by('fecha_ingreso')
    #    if [modulo.codigo for modulo in modulos_ordenados] == ['Modulo I', 'Modulo II', 'Modulo III']:
    #        self.generar_constancia()

    #def generar_constancia(self):
    #    # Crear constancia si aún no existe
    #    Constancia.objects.get_or_create(
    #        estudiante=self.estudiante,
    #        defaults={'codigo_constancia': f"CONST-{self.estudiante.dni}-{timezone.now().year}"}
    #    )



class Constancia(models.Model):
    estudiante = models.OneToOneField(
        'UsuarioPersonalizado',
        on_delete=models.CASCADE,
        related_name='constancia'
    )
    fecha_creacion = models.DateField(default=timezone.now)
    codigo_constancia = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Constancia de {self.estudiante.first_name} {self.estudiante.last_name}"
