import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== DEBUG ====================
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# ==================== SEGURANÇA ====================
SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-temporary-key-for-local-dev-only-2026'
        print("⚠️  Usando SECRET_KEY temporária (apenas para desenvolvimento local)")
    else:
        raise ImproperlyConfigured(
            "A variável SECRET_KEY não foi encontrada no ambiente! "
            "Adicione ela no Railway ou no arquivo .env"
        )

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')

CSRF_TRUSTED_ORIGINS = [
    'https://loja-de-roupas-production.up.railway.app',
    'https://*.railway.app',
    'http://localhost',
    'http://127.0.0.1',
    'https://localhost',
]

# ==================== SITE ID (OBRIGATÓRIO PARA ALLAUTH + GOOGLE) ====================
SITE_ID = 1

# ==================== STRIPE ====================
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# ==================== RECAPTCHA ====================
RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')

# ==================== EMAIL (Brevo) ====================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or 'noreply@sualoja.com'

BREVO_API_KEY = os.getenv('BREVO_API_KEY')

# ==================== CLOUDINARY ====================
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

import cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

# ==================== GOOGLE OAUTH ====================
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_SECRET = os.getenv('GOOGLE_SECRET')

# ==================== MERCADO PAGO ====================
MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN')
MERCADO_PAGO_PUBLIC_KEY = os.getenv('MERCADO_PAGO_PUBLIC_KEY')

# ==================== REDIS ====================
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')

# ==================== APPS ====================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.sites',                    # ← Obrigatório para Allauth

    'core',
    'accounts',

    'channels',
    'phonenumber_field',
    'axes',
    'captcha',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

# ==================== MIDDLEWARE ====================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'axes.middleware.AxesMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# ==================== ALLAUTH CONFIG ====================
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
SOCIALACCOUNT_AUTO_SIGNUP = False          # Evita criar conta automaticamente
SOCIALACCOUNT_LOGIN_ON_GET = True          # Melhora experiência do botão Google

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_SECRET,
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# ==================== URLS E APLICAÇÕES ====================
ROOT_URLCONF = 'loja.urls'
WSGI_APPLICATION = 'loja.wsgi.application'
ASGI_APPLICATION = 'loja.asgi.application'

# ==================== TEMPLATES ====================
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

# ==================== BANCO DE DADOS ====================
import dj_database_url

if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==================== CHANNELS (Redis) ====================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

# ==================== INTERNACIONALIZAÇÃO ====================
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True

# ==================== STATIC & MEDIA ====================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/"

# ==================== AUTH ====================
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'
LOGIN_URL = 'accounts:login'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ==================== AXES ====================
AXES_FAILURE_LIMIT = 8
AXES_COOLOFF_TIME = 180
AXES_RESET_ON_SUCCESS = True

# ==================== SEGURANÇA EM PRODUÇÃO ====================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ==================== SENHA MASTER ====================
ADMIN_MASTER_PASSWORD = os.getenv('ADMIN_MASTER_PASSWORD', 'adminjaques2026')