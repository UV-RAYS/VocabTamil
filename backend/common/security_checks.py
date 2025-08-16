"""
Security validation utilities for VocabTamil
Prevents production secrets from being used in test environments
"""
import os
import logging
import sys
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

# Known production secret patterns (partial matches for security)
PRODUCTION_SECRET_PATTERNS = [
    'AKIA',  # AWS Access Key prefix
    'sk-',   # OpenAI/Stripe secret key prefix
    'xoxb-', # Slack bot token prefix
    'ghp_',  # GitHub personal access token
    'gho_',  # GitHub OAuth token
    'ghu_',  # GitHub user token
    'glpat-', # GitLab personal access token
]

# Production domains that should never appear in test mode
PRODUCTION_DOMAINS = [
    'vocabtamil.com',
    'api.vocabtamil.com',
    'www.vocabtamil.com',
    'prod.vocabtamil.com',
]

# Test-safe values that are allowed
TEST_SAFE_VALUES = [
    'testing-secret-key',
    'test-access-key',
    'test-secret-key',
    'test-client-id',
    'test-client-secret',
    'testadmin',
    'test@example.com',
    'localhost',
    '127.0.0.1',
    'beta.vocabtamil.com',
]


def validate_no_production_secrets():
    """
    Validate that no production secrets are being used in test mode
    """
    is_testing = getattr(settings, 'TESTING', False) or 'test' in sys.argv
    is_debug = getattr(settings, 'DEBUG', False)
    
    if not (is_testing or is_debug):
        return  # Skip validation in production
    
    violations = []
    
    # Check environment variables
    env_vars_to_check = [
        'SECRET_KEY',
        'DB_PASSWORD', 
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'GOOGLE_OAUTH2_CLIENT_ID',
        'GOOGLE_OAUTH2_CLIENT_SECRET',
        'EMAIL_HOST_PASSWORD',
        'SENTRY_DSN',
        'ALLOWED_HOSTS',
    ]
    
    for var_name in env_vars_to_check:
        value = os.getenv(var_name, '')
        if value and not is_test_safe_value(value):
            if contains_production_pattern(value):
                violations.append(f"Environment variable {var_name} contains production-like secret")
    
    # Check Django settings
    settings_to_check = [
        ('SECRET_KEY', settings.SECRET_KEY),
        ('ALLOWED_HOSTS', ','.join(settings.ALLOWED_HOSTS)),
    ]
    
    for setting_name, setting_value in settings_to_check:
        if setting_value and not is_test_safe_value(str(setting_value)):
            if contains_production_pattern(str(setting_value)):
                violations.append(f"Django setting {setting_name} contains production-like value")
    
    # Check for production domains
    for domain in PRODUCTION_DOMAINS:
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        if domain in allowed_hosts:
            violations.append(f"Production domain {domain} found in ALLOWED_HOSTS during testing")
    
    if violations:
        error_msg = "SECURITY VIOLATION: Production secrets detected in test environment!\n"
        error_msg += "\n".join(f"- {violation}" for violation in violations)
        error_msg += "\n\nPlease use .env.testing with safe test values only."
        
        logger.error(error_msg)
        raise ImproperlyConfigured(error_msg)
    
    logger.info("✅ Security validation passed - no production secrets detected")


def contains_production_pattern(value):
    """Check if value contains production secret patterns"""
    value_str = str(value).lower()
    
    # Check for known production patterns
    for pattern in PRODUCTION_SECRET_PATTERNS:
        if pattern.lower() in value_str:
            return True
    
    # Check for production domains
    for domain in PRODUCTION_DOMAINS:
        if domain.lower() in value_str:
            return True
    
    # Check for long random strings (likely real secrets)
    if len(value_str) > 32 and not any(safe in value_str for safe in TEST_SAFE_VALUES):
        # Complex pattern suggests real secret
        has_numbers = any(c.isdigit() for c in value_str)
        has_letters = any(c.isalpha() for c in value_str)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in value_str)
        
        if sum([has_numbers, has_letters, has_special]) >= 2:
            return True
    
    return False


def is_test_safe_value(value):
    """Check if value is a known test-safe value"""
    value_str = str(value).lower()
    
    # Check against known safe test values
    for safe_value in TEST_SAFE_VALUES:
        if safe_value.lower() in value_str:
            return True
    
    # Allow empty values
    if not value_str or value_str in ['', 'none', 'null', 'false']:
        return True
    
    return False


def sanitize_log_data(data):
    """
    Sanitize sensitive data from logs
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if is_sensitive_field(key):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, (dict, list)):
                sanitized[key] = sanitize_log_data(value)
            else:
                sanitized[key] = value
        return sanitized
    
    elif isinstance(data, list):
        return [sanitize_log_data(item) for item in data]
    
    elif isinstance(data, str):
        # Sanitize potential secrets in strings
        if contains_production_pattern(data):
            return '[REDACTED]'
        return data
    
    return data


def is_sensitive_field(field_name):
    """Check if field name indicates sensitive data"""
    sensitive_keywords = [
        'password', 'secret', 'key', 'token', 'auth', 'credential',
        'private', 'confidential', 'secure', 'api_key', 'access_key',
        'client_secret', 'oauth', 'jwt', 'session', 'cookie'
    ]
    
    field_lower = field_name.lower()
    return any(keyword in field_lower for keyword in sensitive_keywords)


class SecureLoggingFilter(logging.Filter):
    """
    Logging filter to sanitize sensitive data from logs
    """
    
    def filter(self, record):
        # Sanitize the log message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self.sanitize_message(record.msg)
        
        # Sanitize arguments
        if hasattr(record, 'args') and record.args:
            record.args = tuple(
                '[REDACTED]' if isinstance(arg, str) and contains_production_pattern(arg) else arg
                for arg in record.args
            )
        
        return True
    
    def sanitize_message(self, message):
        """Sanitize sensitive data from log messages"""
        # Replace potential secrets with redacted placeholder
        words = message.split()
        sanitized_words = []
        
        for word in words:
            if contains_production_pattern(word):
                sanitized_words.append('[REDACTED]')
            else:
                sanitized_words.append(word)
        
        return ' '.join(sanitized_words)


def setup_secure_logging():
    """Setup secure logging with sensitive data filtering"""
    # Add secure logging filter to all handlers
    secure_filter = SecureLoggingFilter()
    
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(secure_filter)
    
    # Add to Django loggers
    django_logger = logging.getLogger('django')
    for handler in django_logger.handlers:
        handler.addFilter(secure_filter)


# Runtime configuration validation
def validate_runtime_config():
    """Validate runtime configuration for security"""
    issues = []
    
    # Check if we're accidentally in production mode during testing
    if 'test' in sys.argv and not getattr(settings, 'DEBUG', False):
        issues.append("Running tests in production mode (DEBUG=False)")
    
    # Check database configuration
    db_config = settings.DATABASES.get('default', {})
    if 'test' in sys.argv and 'sqlite' not in db_config.get('ENGINE', ''):
        issues.append("Tests should use SQLite for isolation")
    
    # Check cache configuration
    cache_config = settings.CACHES.get('default', {})
    if 'test' in sys.argv and 'locmem' not in cache_config.get('BACKEND', ''):
        issues.append("Tests should use local memory cache")
    
    if issues:
        warning_msg = "⚠️  Configuration warnings:\n" + "\n".join(f"- {issue}" for issue in issues)
        logger.warning(warning_msg)
    
    return len(issues) == 0
