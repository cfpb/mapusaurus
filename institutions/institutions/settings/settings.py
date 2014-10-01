"""
Django settings for institutions project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '($2ob)%vv$wv7jl-$e!=#z!+bhihs@o%$+@c0yqrz&8*f@#hhi'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.humanize',
    'localflavor',
    'south',
    'leaflet',
    'haystack',
    'rest_framework',
    'basestyle',
    'mapping',
    'respondants',
    'geo',
    'censusdata',
    'hmda',
    'batch',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'institutions.urls'

WSGI_APPLICATION = 'institutions.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {'default': {'ENGINE': '', 'NAME': '', 'USER': '', 'PASSWORD': ''}}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'

LEAFLET_CONFIG = {
    'RESET_VIEW': False,
    'TILES': 'http://tile.stamen.com/toner-lite/{z}/{x}/{y}.jpg',
    'SCALE': 'imperial',
    'MIN_ZOOM': 7,
    'MAX_ZOOM': 18
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'mapusaurus',
    },
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.TemplateHTMLRenderer',
        'rest_framework.renderers.JSONRenderer',
    ],
}

SOUTH_TESTS_MIGRATE = False

LONGTERM_CACHE_TIMEOUT = 60*60*24*30   # 30 days

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'long_term_geos': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/long_term_geos',
        'TIMEOUT': LONGTERM_CACHE_TIMEOUT,
        'OPTIONS': {
            'MAX_ENTRIES': 1000000
        }
    }
}

if 'test' in sys.argv:
    CACHES['long_term_geos']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'

CONTACT_US_EMAIL = 'feedback@example.com'

from institutions.settings.local_settings import *
