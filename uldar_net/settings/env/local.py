# Project modules
from settings.base import *


DEBUG = True
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost"
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    },
}