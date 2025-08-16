"""
Test-specific Django settings for VocabTamil
Secure configuration for testing environments
"""
from .settings import *
import os

# Override settings for testing
DEBUG = True
TESTING = True

# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable real external services
AWS_S3_CUSTOM_DOMAIN = None
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Use fake Redis for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Disable Celery for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Security settings for testing
SECRET_KEY = 'testing-secret-key-for-development-only'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', 'beta.vocabtamil.com']

# Disable rate limiting for tests
RATE_LIMIT_ENABLED = False

# Performance settings for testing
SLOW_QUERY_THRESHOLD = float(os.getenv('SLOW_QUERY_THRESHOLD', '2.0'))

# Analytics disabled for testing
ANALYTICS_ENABLED = False

# Mock external services
MOCK_EXTERNAL_SERVICES = True

# Logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'vocabtamil': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# Password validation (simplified for testing)
AUTH_PASSWORD_VALIDATORS = []

# Disable CORS checks for testing
CORS_ALLOW_ALL_ORIGINS = True

# JWT settings for testing
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Longer for testing
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
})

# Media files for testing
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')

# Static files for testing
STATIC_ROOT = os.path.join(BASE_DIR, 'test_static')

# Test-specific middleware (remove rate limiting)
MIDDLEWARE = [m for m in MIDDLEWARE if 'RateLimitMiddleware' not in m]
