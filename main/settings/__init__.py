import os

ENVIRONMENT = os.getenv('DJANGO_ENV', 'dev')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .dev import *