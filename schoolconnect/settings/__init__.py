from decouple import config

if config('ENVIRONMENT', default='development') == 'production':
    from .production import *
else:
    from .development import * 