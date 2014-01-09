import os
import dj_database_url


DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}

DEBUG = True
TEMPLATE_DEBUG = DEBUG

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': os.environ['BONSAI_URL'],
        'INDEX_NAME': 'documents',
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
LOGIN_REDIRECT_URL = ''

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
ACCOUNT_ACTIVATION_DAYS = 7
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = ''

STATIC_URL = '/https://s3.amazonaws.com/colibrifp7/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.linkedin',
    #    'allauth.socialaccount.providers.openid',
    'allauth.socialaccount.providers.google',
    'tagging',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'fluent_comments',
    'crispy_forms',
    'django.contrib.comments',
    'colibri',
    "colibri.athumb",
    'storages',
    'crispy_forms',
    'organizations',
    'tastypie',
    'ajax_validation',
    'djangoratings',
    'django_countries',
    'voting',
    'haystack',
    'django.contrib.humanize',
    'south',
    'django_notify',
    'mptt',
    'sekizai',
    'sorl.thumbnail',
    'wiki',
    'wiki.plugins.macros',
    'wiki.plugins.help',
    'wiki.plugins.links',
    'wiki.plugins.images',
    'wiki.plugins.attachments',
    'wiki.plugins.notifications',
    'messages',
)
