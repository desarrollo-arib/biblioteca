# settings/production.py
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['biblioteca-gobz.onrender.com']


# Configuración de base de datos de producción
DATABASES = {
    'default': env.db("DATABASE_URL")
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Seguridad para producción
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True