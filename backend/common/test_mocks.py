"""
Centralized mocking utilities for VocabTamil testing
Prevents accidental real external service calls
"""
import os
from unittest.mock import Mock, patch, MagicMock
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MockExternalServices:
    """Centralized mock manager for all external services"""
    
    def __init__(self):
        self.active_patches = []
        self.is_mocking_enabled = getattr(settings, 'MOCK_EXTERNAL_SERVICES', True)
    
    def start_all_mocks(self):
        """Start all external service mocks"""
        if not self.is_mocking_enabled:
            return
        
        logger.info("🔧 Starting external service mocks for testing")
        
        # AWS S3 Mocks
        self._mock_aws_s3()
        
        # Email Mocks
        self._mock_email_backend()
        
        # Google OAuth Mocks
        self._mock_google_oauth()
        
        # Analytics Mocks
        self._mock_analytics()
        
        # Redis Mocks (if not using fakeredis)
        self._mock_redis()
        
        # HTTP Request Mocks
        self._mock_external_http()
    
    def stop_all_mocks(self):
        """Stop all active mocks"""
        for patcher in self.active_patches:
            try:
                patcher.stop()
            except Exception as e:
                logger.warning(f"Failed to stop mock: {e}")
        
        self.active_patches.clear()
        logger.info("🛑 Stopped all external service mocks")
    
    def _mock_aws_s3(self):
        """Mock AWS S3 operations"""
        # Mock boto3 S3 client
        s3_mock = Mock()
        s3_mock.upload_file.return_value = None
        s3_mock.upload_fileobj.return_value = None
        s3_mock.delete_object.return_value = None
        s3_mock.generate_presigned_url.return_value = 'http://localhost:8000/test-audio.mp3'
        
        boto3_patch = patch('boto3.client')
        boto3_mock = boto3_patch.start()
        boto3_mock.return_value = s3_mock
        
        self.active_patches.append(boto3_patch)
        
        # Mock Django S3 storage
        storage_patch = patch('storages.backends.s3boto3.S3Boto3Storage.save')
        storage_mock = storage_patch.start()
        storage_mock.return_value = 'test-file.mp3'
        
        self.active_patches.append(storage_patch)
    
    def _mock_email_backend(self):
        """Mock email sending"""
        email_patch = patch('django.core.mail.send_mail')
        email_mock = email_patch.start()
        email_mock.return_value = True
        
        self.active_patches.append(email_patch)
        
        # Mock mass email
        mass_email_patch = patch('django.core.mail.send_mass_mail')
        mass_email_mock = mass_email_patch.start()
        mass_email_mock.return_value = 1
        
        self.active_patches.append(mass_email_patch)
    
    def _mock_google_oauth(self):
        """Mock Google OAuth operations"""
        # Mock Google OAuth token verification
        oauth_patch = patch('google.oauth2.id_token.verify_oauth2_token')
        oauth_mock = oauth_patch.start()
        oauth_mock.return_value = {
            'sub': 'test-google-user-id',
            'email': 'testuser@gmail.com',
            'name': 'Test User',
            'given_name': 'Test',
            'family_name': 'User',
        }
        
        self.active_patches.append(oauth_patch)
    
    def _mock_analytics(self):
        """Mock analytics and monitoring services"""
        # Mock Sentry
        sentry_patch = patch('sentry_sdk.capture_exception')
        sentry_mock = sentry_patch.start()
        sentry_mock.return_value = None
        
        self.active_patches.append(sentry_patch)
        
        # Mock custom analytics
        analytics_patch = patch('requests.post')
        analytics_mock = analytics_patch.start()
        analytics_mock.return_value.status_code = 200
        analytics_mock.return_value.json.return_value = {'success': True}
        
        self.active_patches.append(analytics_patch)
    
    def _mock_redis(self):
        """Mock Redis operations if not using fakeredis"""
        if 'fakeredis' not in str(settings.CACHES.get('default', {}).get('BACKEND', '')):
            redis_patch = patch('redis.Redis')
            redis_mock = redis_patch.start()
            
            # Create a simple in-memory store
            mock_store = {}
            
            def mock_get(key):
                return mock_store.get(key)
            
            def mock_set(key, value, ex=None):
                mock_store[key] = value
                return True
            
            def mock_delete(key):
                return mock_store.pop(key, None) is not None
            
            redis_instance = Mock()
            redis_instance.get = mock_get
            redis_instance.set = mock_set
            redis_instance.delete = mock_delete
            redis_instance.exists.return_value = True
            
            redis_mock.return_value = redis_instance
            self.active_patches.append(redis_patch)
    
    def _mock_external_http(self):
        """Mock external HTTP requests"""
        # Mock requests library
        requests_patch = patch('requests.get')
        requests_mock = requests_patch.start()
        
        # Default successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'data': 'test'}
        mock_response.text = 'test response'
        
        requests_mock.return_value = mock_response
        self.active_patches.append(requests_patch)


# Global mock manager instance
mock_manager = MockExternalServices()


def setup_test_mocks():
    """Setup all test mocks - call this in test setup"""
    mock_manager.start_all_mocks()


def teardown_test_mocks():
    """Teardown all test mocks - call this in test teardown"""
    mock_manager.stop_all_mocks()


class MockAudioService:
    """Mock audio service for testing"""
    
    @staticmethod
    def generate_tts_audio(text, language='ta'):
        """Mock TTS audio generation"""
        return f"mock-audio-{text[:10]}.mp3"
    
    @staticmethod
    def upload_audio_file(file_path):
        """Mock audio file upload"""
        return f"http://localhost:8000/test-audio/{os.path.basename(file_path)}"
    
    @staticmethod
    def validate_audio_file(file_path):
        """Mock audio file validation"""
        return {
            'valid': True,
            'duration': 2.5,
            'format': 'mp3',
            'quality': 'good'
        }


class MockPaymentService:
    """Mock payment service for future premium features"""
    
    @staticmethod
    def create_subscription(user_id, plan_id):
        """Mock subscription creation"""
        return {
            'subscription_id': f'test-sub-{user_id}',
            'status': 'active',
            'plan': plan_id
        }
    
    @staticmethod
    def cancel_subscription(subscription_id):
        """Mock subscription cancellation"""
        return {'status': 'cancelled'}


class MockNotificationService:
    """Mock notification service"""
    
    @staticmethod
    def send_push_notification(user_id, message):
        """Mock push notification"""
        logger.info(f"Mock push notification to {user_id}: {message}")
        return {'sent': True, 'message_id': f'test-msg-{user_id}'}
    
    @staticmethod
    def send_email_notification(email, subject, message):
        """Mock email notification"""
        logger.info(f"Mock email to {email}: {subject}")
        return {'sent': True, 'email_id': f'test-email-{hash(email)}'}


# Context managers for specific service mocking
class MockS3Context:
    """Context manager for S3 mocking"""
    
    def __enter__(self):
        self.patcher = patch('boto3.client')
        self.mock = self.patcher.start()
        
        s3_mock = Mock()
        s3_mock.upload_file.return_value = None
        s3_mock.generate_presigned_url.return_value = 'http://localhost:8000/test.mp3'
        
        self.mock.return_value = s3_mock
        return s3_mock
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.patcher.stop()


class MockEmailContext:
    """Context manager for email mocking"""
    
    def __enter__(self):
        self.patcher = patch('django.core.mail.send_mail')
        self.mock = self.patcher.start()
        self.mock.return_value = True
        return self.mock
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.patcher.stop()


# Decorator for automatic mock setup/teardown
def with_mocked_services(test_func):
    """Decorator to automatically setup and teardown mocks for a test"""
    def wrapper(*args, **kwargs):
        setup_test_mocks()
        try:
            return test_func(*args, **kwargs)
        finally:
            teardown_test_mocks()
    
    return wrapper


# Validation functions
def ensure_no_real_calls():
    """Ensure no real external calls are made during testing"""
    if not getattr(settings, 'TESTING', False):
        return
    
    # Check for common signs of real external calls
    warning_indicators = [
        ('AWS_ACCESS_KEY_ID', lambda x: x and not x.startswith('test-')),
        ('GOOGLE_OAUTH2_CLIENT_ID', lambda x: x and not x.startswith('test-')),
        ('SENTRY_DSN', lambda x: x and 'sentry.io' in x),
    ]
    
    for env_var, check_func in warning_indicators:
        value = os.getenv(env_var, '')
        if check_func(value):
            logger.warning(f"⚠️  {env_var} may contain real credentials in test environment")


# Auto-setup for Django tests
def setup_django_test_mocks():
    """Setup mocks specifically for Django tests"""
    if 'test' in os.sys.argv:
        setup_test_mocks()
        ensure_no_real_calls()
        logger.info("✅ Django test mocks activated")
