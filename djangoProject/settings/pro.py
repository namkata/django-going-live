import os
from .base import *
DEBUG = False
ADMINS = (
    ('root', 'root@example.com')
)
ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'educa',
        'USER': 'educa',
        'PASSWORD': '*********'
    }
}
