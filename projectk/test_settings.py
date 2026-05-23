from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SECRET_KEY = 'test-secret-key-for-pytest-do-not-use-in-production'
DEBUG = True
STATICFILES_DIRS = []
