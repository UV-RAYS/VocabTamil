"""
Performance monitoring and optimization utilities for VocabTamil
"""
import time
import logging
from functools import wraps
from django.core.cache import cache
from django.db import connection
from django.conf import settings
import psutil
import os
from django.conf import settings

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.metrics = {}
        # Make slow query threshold configurable for testing
        self.slow_query_threshold = float(os.getenv('SLOW_QUERY_THRESHOLD', '0.5'))  # 500ms default
        
    def timing_decorator(self, operation_name):
        """Decorator to time function execution"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Log slow operations
                    if execution_time > self.slow_query_threshold:
                        logger.warning(f"Slow operation: {operation_name} took {execution_time:.3f}s")
                    
                    # Store metrics
                    self.record_metric(operation_name, execution_time)
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Operation failed: {operation_name} took {execution_time:.3f}s - {str(e)}")
                    raise
            return wrapper
        return decorator
    
    def record_metric(self, operation, duration):
        """Record performance metric"""
        # Skip recording in test mode if disabled
        if getattr(settings, 'TESTING', False) and not getattr(settings, 'RECORD_METRICS', True):
            return
            
        if operation not in self.metrics:
            self.metrics[operation] = []
        
        self.metrics[operation].append({
            'duration': duration,
            'timestamp': time.time()
        })
        
        # Keep only last 100 measurements
        if len(self.metrics[operation]) > 100:
            self.metrics[operation] = self.metrics[operation][-100:]
    
    def get_metrics_summary(self):
        """Get performance metrics summary"""
        summary = {}
        for operation, measurements in self.metrics.items():
            if measurements:
                durations = [m['duration'] for m in measurements]
                summary[operation] = {
                    'count': len(durations),
                    'avg_duration': sum(durations) / len(durations),
                    'max_duration': max(durations),
                    'min_duration': min(durations),
                    'slow_queries': len([d for d in durations if d > self.slow_query_threshold])
                }
        return summary


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name):
    """Decorator for monitoring function performance"""
    return performance_monitor.timing_decorator(operation_name)


def get_system_metrics():
    """Get system performance metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available / (1024 * 1024),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024 * 1024 * 1024)
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {str(e)}")
        return {}


def get_database_metrics():
    """Get database performance metrics"""
    try:
        queries = connection.queries
        total_time = sum(float(query['time']) for query in queries)
        slow_queries = [q for q in queries if float(q['time']) > 0.1]
        
        return {
            'total_queries': len(queries),
            'total_time': total_time,
            'slow_queries': len(slow_queries),
            'avg_query_time': total_time / len(queries) if queries else 0,
            'slowest_query_time': max(float(q['time']) for q in queries) if queries else 0
        }
    except Exception as e:
        logger.error(f"Failed to get database metrics: {str(e)}")
        return {}


class CacheOptimizer:
    """Cache optimization utilities"""
    
    @staticmethod
    def cache_with_timeout(key, timeout=300):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key from function name and args
                cache_key = f"{key}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                result = cache.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def invalidate_cache_pattern(pattern):
        """Invalidate cache keys matching pattern"""
        try:
            # This is Redis-specific - adapt for other cache backends
            from django.core.cache import cache
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'delete_pattern'):
                cache._cache.delete_pattern(pattern)
        except Exception as e:
            logger.warning(f"Cache invalidation failed: {str(e)}")


class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def optimize_word_queries():
        """Optimize common word-related queries"""
        from vocabulary.models import Word, UserWordProgress
        
        # Prefetch related data to avoid N+1 queries
        return Word.objects.select_related().prefetch_related(
            'userwordprogress_set'
        )
    
    @staticmethod
    def optimize_quiz_queries():
        """Optimize quiz-related queries"""
        from quizzes.models import QuizSession, QuizQuestion
        
        return QuizSession.objects.select_related('user').prefetch_related(
            'questions__word'
        )
    
    @staticmethod
    def optimize_progress_queries(user):
        """Optimize progress queries for a user"""
        from vocabulary.models import UserWordProgress
        
        return UserWordProgress.objects.filter(user=user).select_related(
            'word'
        ).order_by('-last_reviewed')


def batch_database_operations(operations, batch_size=100):
    """Execute database operations in batches"""
    for i in range(0, len(operations), batch_size):
        batch = operations[i:i + batch_size]
        try:
            # Execute batch
            for operation in batch:
                operation()
        except Exception as e:
            logger.error(f"Batch operation failed: {str(e)}")


class APIRateLimiter:
    """Simple in-memory rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests = {}
        self.cleanup_interval = 60  # seconds
        self.last_cleanup = time.time()
    
    def is_allowed(self, key, limit, window):
        """Check if request is allowed under rate limit"""
        now = time.time()
        
        # Cleanup old entries periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self.cleanup_old_entries(now - window)
            self.last_cleanup = now
        
        # Get request history for this key
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key] 
            if now - req_time < window
        ]
        
        # Check if under limit
        if len(self.requests[key]) < limit:
            self.requests[key].append(now)
            return True
        
        return False
    
    def cleanup_old_entries(self, cutoff_time):
        """Remove old entries to prevent memory leaks"""
        for key in list(self.requests.keys()):
            self.requests[key] = [
                req_time for req_time in self.requests[key] 
                if req_time > cutoff_time
            ]
            if not self.requests[key]:
                del self.requests[key]


# Global rate limiter instance
api_rate_limiter = APIRateLimiter()


def performance_test_endpoint(view_func):
    """Decorator to add performance testing to API endpoints"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        start_queries = len(connection.queries)
        
        response = view_func(request, *args, **kwargs)
        
        end_time = time.time()
        end_queries = len(connection.queries)
        
        duration = end_time - start_time
        query_count = end_queries - start_queries
        
        # Log performance metrics
        if duration > 1.0 or query_count > 10:
            logger.warning(
                f"Slow endpoint: {request.path} - "
                f"Duration: {duration:.3f}s, Queries: {query_count}"
            )
        
        # Add performance headers in debug mode
        if settings.DEBUG:
            response['X-Response-Time'] = f"{duration:.3f}s"
            response['X-Query-Count'] = str(query_count)
        
        return response
    
    return wrapper


def memory_usage_monitor():
    """Monitor memory usage and log warnings"""
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)
        
        if memory_mb > 500:  # 500MB threshold
            logger.warning(f"High memory usage: {memory_mb:.1f}MB")
        
        return memory_mb
    except Exception as e:
        logger.error(f"Memory monitoring failed: {str(e)}")
        return 0


# Performance monitoring middleware
class PerformanceMiddleware:
    """Middleware to monitor API performance"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        start_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        query_count = len(connection.queries) - start_queries
        
        # Record metrics
        performance_monitor.record_metric('api_request', duration)
        
        # Log slow requests
        if duration > 2.0:
            logger.warning(
                f"Slow request: {request.method} {request.path} - "
                f"Duration: {duration:.3f}s, Queries: {query_count}"
            )
        
        return response
