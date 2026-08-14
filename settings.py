"""
Django settings for CCMS (Community Contribution Management System).

Environment-variable driven so the same codebase runs unmodified in:
  - local development (SQLite, zero config)
  - shared hosting via cPanel — Hostinger, Bluehost, GoDaddy, Namecheap,
    HostGator, and most other cPanel-based hosts — via Passenger + MySQL.
    See DEPLOYMENT.md at the project root for step-by-step setup.

Every setting below falls back to a sensible local-dev default if the
corresponding environment variable isn't set, so `python manage.py
runserver` keeps working with zero configuration.
"""
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent

# SECURITY WARNING: set a real, unique SECRET_KEY via the SECRET_KEY env var in production!
SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-CHANGE-THIS-SECRET-KEY-IN-PRODUCTION-abc123xyz',
)

# SECURITY WARNING: don't run with DEBUG=True in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # CCMS apps
    'accounts',
    'communities',
    'houses',
    'contributors',
    'payments',
    'dashboard',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serves static files without needing nginx — ideal for shared hosting
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'config.context_processors.role_flags',
                'config.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------------------------
# Database — defaults to SQLite for zero-config local dev. On shared hosting
# (Hostinger/Bluehost/GoDaddy/any cPanel host), create a MySQL database in
# cPanel and set DB_ENGINE=mysql plus the DB_* variables below (see
# DEPLOYMENT.md).
# ---------------------------------------------------------------------------
if config('DB_ENGINE', default='sqlite') == 'mysql':
    import pymysql
    pymysql.install_as_MySQLdb()  # pure-Python MySQL driver — no C compiler needed on shared hosting

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='3306'),
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Accra'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Compressed + hashed filenames in production; falls back to plain serving in
# dev so `runserver` works without needing `collectstatic` first.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage' if not DEBUG
        else 'django.contrib.staticfiles.storage.StaticFilesStorage'
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Session: "Remember me" toggles this per-login in the view
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 14 days when remember-me is checked
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Shared hosting is almost always served over HTTPS via the host's proxy/cPanel SSL —
# these keep Django's own security headers correct behind that proxy in production.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)

# Hardened cookie/browser defaults - safe in both dev and prod.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# ---------------------------------------------------------------------------
# SMS Gateway configuration — swap provider/credentials via environment
# variables; implement the actual HTTP call for your provider in accounts/sms.py.
# ---------------------------------------------------------------------------
SMS_PROVIDER = config('SMS_PROVIDER', default='console')  # 'console' logs to terminal — safe default for dev
SMS_API_KEY = config('SMS_API_KEY', default='')
SMS_SENDER_ID = config('SMS_SENDER_ID', default='CCMS')

# Community-wide currency symbol used across templates
CURRENCY_SYMBOL = 'GH₵'
