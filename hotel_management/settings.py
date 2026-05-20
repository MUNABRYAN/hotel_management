"""
Django settings for hotel_management project.
Configuración profesional para FASE 1 del sistema hotelero.
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# SEGURIDAD - Claves secretas y debug
# =============================================================================
SECRET_KEY = 'django-insecure-cambiar-en-produccion-poner-en-variables-de-entorno'
DEBUG = True  # En producción: False
ALLOWED_HOSTS = ['*']  # En producción: ['midominio.com', 'www.midominio.com']

# =============================================================================
# APLICACIONES INSTALADAS
# Orden: Django built-in → Terceros → Propias
# =============================================================================
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'temporadas.apps.TemporadasConfig',
    'restaurant.apps.RestaurantConfig',

    # Terceros (para futuras fases)
    # 'rest_framework',  # Descomentar en FASE 2
    'imagekit',  # Thumbnails automáticos de fotos

    # Apps propias
    'core.apps.CoreConfig',
    'hotel.apps.HotelConfig',
    'usuarios.apps.UsuariosConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hotel_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Carpeta global de templates
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

WSGI_APPLICATION = 'hotel_management.wsgi.application'

# =============================================================================
# BASE DE DATOS
# Desarrollo: SQLite | Producción: PostgreSQL
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =============================================================================
# AUTENTICACIÓN PERSONALIZADA
# Usamos nuestro propio modelo de usuario con roles
# =============================================================================
AUTH_USER_MODEL = 'usuarios.UsuarioPersonalizado'

# =============================================================================
# INTERNACIONALIZACIÓN
# Zona horaria de Venezuela (puedes cambiarla)
# =============================================================================
LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

# =============================================================================
# ARCHIVOS ESTÁTICOS (CSS, JS, Imágenes de diseño)
# =============================================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Para collectstatic en producción

# =============================================================================
# ARCHIVOS MEDIA (Subidos por usuarios: fotos de habitaciones, huéspedes)
# =============================================================================
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# TIPO DE CAMPO POR DEFECTO
# Evita migraciones innecesarias en Django 5.x
# =============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# CONFIGURACIÓN DE IMAGEKIT (Thumbnails automáticos)
# =============================================================================
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = 'imagekit.cachefiles.strategies.Optimistic'


# =============================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN
# =============================================================================
LOGIN_URL = 'usuarios:login'  # A dónde redirigir si no está autenticado
LOGIN_REDIRECT_URL = 'hotel:dashboard'  # A dónde ir después de login exitoso
LOGOUT_REDIRECT_URL = 'usuarios:login'  # A dónde ir después de logout