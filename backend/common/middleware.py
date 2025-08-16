"""
Security and monitoring middleware for VocabTamil
"""
import time
import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware to prevent abuse"""
    
    def process_request(self, request):
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Different limits for different endpoints
        if request.path.startswith('/api/v1/auth/'):
            # Stricter limits for auth endpoints
            limit = getattr(settings, 'AUTH_RATE_LIMIT', 5)  # 5 requests per minute
            window = 60
        elif request.path.startswith('/api/v1/quiz/'):
            # Moderate limits for quiz endpoints
            limit = getattr(settings, 'QUIZ_RATE_LIMIT', 30)  # 30 requests per minute
            window = 60
        else:
            # General API limits
            limit = getattr(settings, 'API_RATE_LIMIT', 100)  # 100 requests per minute
            window = 60
        
        # Check rate limit
        cache_key = f"rate_limit:{ip}:{request.path_info.split('/')[1]}"
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= limit:
            logger.warning(f"Rate limit exceeded for IP {ip} on {request.path}")
            return JsonResponse({
                'error': 'rate_limit_exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': window
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, window)
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to responses"""
    
    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # HSTS for HTTPS
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log requests for monitoring and debugging"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log API requests
        if request.path.startswith('/api/'):
            logger.info(f"API Request: {request.method} {request.path} from {self.get_client_ip(request)}")
        
        return None
    
    def process_response(self, request, response):
        # Log response time for API requests
        if hasattr(request, 'start_time') and request.path.startswith('/api/'):
            duration = time.time() - request.start_time
            
            # Log slow requests
            if duration > 2.0:  # 2 seconds
                logger.warning(f"Slow API request: {request.method} {request.path} took {duration:.2f}s")
            
            # Log errors
            if response.status_code >= 400:
                logger.error(f"API Error: {request.method} {request.path} returned {response.status_code}")
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class BruteForceProtectionMiddleware(MiddlewareMixin):
    """Protect against brute force attacks on login"""
    
    def process_request(self, request):
        # Only check login attempts
        if request.path == '/api/v1/auth/login/' and request.method == 'POST':
            ip = self.get_client_ip(request)
            
            # Check failed login attempts
            failed_attempts_key = f"failed_login:{ip}"
            failed_attempts = cache.get(failed_attempts_key, 0)
            
            # Block after 5 failed attempts
            if failed_attempts >= 5:
                logger.warning(f"Brute force protection triggered for IP {ip}")
                return JsonResponse({
                    'error': 'too_many_failed_attempts',
                    'message': 'Too many failed login attempts. Please try again later.',
                    'retry_after': 900  # 15 minutes
                }, status=429)
        
        return None
    
    def process_response(self, request, response):
        # Track failed login attempts
        if request.path == '/api/v1/auth/login/' and request.method == 'POST':
            ip = self.get_client_ip(request)
            failed_attempts_key = f"failed_login:{ip}"
            
            if response.status_code == 401:  # Unauthorized
                # Increment failed attempts
                failed_attempts = cache.get(failed_attempts_key, 0)
                cache.set(failed_attempts_key, failed_attempts + 1, 900)  # 15 minutes
            elif response.status_code == 200:  # Success
                # Clear failed attempts on successful login
                cache.delete(failed_attempts_key)
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DatabaseTransactionMiddleware(MiddlewareMixin):
    """Handle race conditions in database transactions"""
    
    def process_exception(self, request, exception):
        # Log database-related exceptions
        if 'database' in str(exception).lower() or 'integrity' in str(exception).lower():
            logger.error(f"Database error in {request.path}: {str(exception)}")
            
            return JsonResponse({
                'error': 'database_error',
                'message': 'A database error occurred. Please try again.'
            }, status=500)
        
        return None
