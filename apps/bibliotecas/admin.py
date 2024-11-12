from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPersonalizado
from .forms import UsuarioPersonalizadoCreationForm, UsuarioPersonalizadoChangeForm

class UsuarioPersonalizadoAdmin(UserAdmin):
    add_form = UsuarioPersonalizadoCreationForm
    form = UsuarioPersonalizadoChangeForm
    model = UsuarioPersonalizado
    list_display = ('email', 'first_name', 'last_name', 'dni', 'programa_estudio', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'programa_estudio', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'dni', 'programa_estudio', 'rol')}),
        ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'dni', 'programa_estudio', 'rol', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name', 'dni')
    ordering = ('email',)

admin.site.register(UsuarioPersonalizado, UsuarioPersonalizadoAdmin)