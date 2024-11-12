from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def rol_requerido(roles_permitidos=[]):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.perfil.rol in roles_permitidos:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('no_autorizado')
        return _wrapped_view
    return decorator