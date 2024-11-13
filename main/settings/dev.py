# settings/dev.py
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['biblioteca-gobz.onrender.com','localhost', '127.0.0.1']

# Configuración de base de datos para desarrollo local
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

# Configuración de archivos estáticos en desarrollo
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'