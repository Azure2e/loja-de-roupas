import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-sualoja1234567890abcdef'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'core',
    'accounts',
    'phonenumber_field',
    'axes',                     # ← Proteção contra força bruta
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',   # ← DEVE ficar DEPOIS do AuthenticationMiddleware
]

ROOT_URLCONF = 'loja.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'loja.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'
LOGIN_URL = 'accounts:login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== CONFIGURAÇÃO DE EMAIL - BREVO ====================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'xsmtpsib-79a55c787843087a80c2ea2ab87db194caf434887f91c2865e58c0b05f8ae076-iWHwlCHPyjEppDXu'
EMAIL_HOST_PASSWORD = 'xsmtpsib-79a55c787843087a80c2ea2ab87db194caf434887f91c2865e58c0b05f8ae076-iWHwlCHPyjEppDXu'
DEFAULT_FROM_EMAIL = 'SuaLoja <noreply@sualoja.com>'

# ==================== MERCADO PAGO ====================
MERCADO_PAGO_ACCESS_TOKEN = 'APP_USR-7903155224263403-033112-d0e37f13af0fe2563342a70b4b76cd69-567886674'
MERCADO_PAGO_PUBLIC_KEY   = 'APP_USR-f532bfd5-c5a2-4d31-835f-4520b1fa94b1'

# ==================== BREVO WHATSAPP ====================
BREVO_API_KEY = 'xsmtpsib-79a55c787843087a80c2ea2ab87db194caf434887f91c2865e58c0b05f8ae076-iWHwlCHPyjEppDXu'
WHATSAPP_SENDER = '556881178014'

# ==================== PROTEÇÃO CONTRA FORÇA BRUTA (django-axes) ====================
AXES_FAILURE_LIMIT = 5              # Máximo de 5 tentativas erradas
AXES_LOCKOUT_DURATION = 30          # Bloqueia por 30 minutos
AXES_RESET_ON_SUCCESS = True        # Reseta o contador após login correto
AXES_COOLOFF_TIME = 30              # Tempo de espera em minutos
AXES_VERBOSE = True                 # Mostra logs detalhados no terminal
AXES_LOCKOUT_TEMPLATE = 'axes/lockout.html'

# ==================== SENHA EXTRA PARA O ADMIN ====================
ADMIN_MASTER_PASSWORD = 'adminjaques2026'   # ← Mude para uma senha forte!

# ==================== AUTHENTICATION BACKENDS (obrigatório para django-axes) ====================
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',   # ← Proteção contra força bruta
    'django.contrib.auth.backends.ModelBackend',   # ← Login normal do Django
]