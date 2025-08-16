"""
Custom exceptions and error handlers for VocabTamil
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


class VocabTamilException(Exception):
    """Base exception for VocabTamil application"""
    pass


class QuizSessionError(VocabTamilException):
    """Quiz session related errors"""
    pass


class WordProgressError(VocabTamilException):
    """Word progress related errors"""
    pass


class AchievementError(VocabTamilException):
    """Achievement related errors"""
    pass


class NetworkTimeoutError(VocabTamilException):
    """Network timeout errors"""
    pass


def custom_exception_handler(exc, context):
    """Custom exception handler for API responses"""
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception
    request = context.get('request')
    if request:
        logger.error(f"API Exception in {request.path}: {str(exc)}", exc_info=True)
    
    # Handle custom exceptions
    if isinstance(exc, QuizSessionError):
        return Response({
            'error': 'quiz_session_error',
            'message': str(exc),
            'code': 'QUIZ_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, WordProgressError):
        return Response({
            'error': 'word_progress_error',
            'message': str(exc),
            'code': 'PROGRESS_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, AchievementError):
        return Response({
            'error': 'achievement_error',
            'message': str(exc),
            'code': 'ACHIEVEMENT_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, NetworkTimeoutError):
        return Response({
            'error': 'network_timeout',
            'message': 'Request timed out. Please try again.',
            'code': 'TIMEOUT_ERROR',
            'retry_after': 30
        }, status=status.HTTP_408_REQUEST_TIMEOUT)
    
    elif isinstance(exc, IntegrityError):
        return Response({
            'error': 'data_integrity_error',
            'message': 'A data integrity error occurred. Please try again.',
            'code': 'INTEGRITY_ERROR'
        }, status=status.HTTP_409_CONFLICT)
    
    elif isinstance(exc, ValidationError):
        return Response({
            'error': 'validation_error',
            'message': str(exc),
            'code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle database connection errors
    elif 'database' in str(exc).lower():
        return Response({
            'error': 'database_error',
            'message': 'Database temporarily unavailable. Please try again.',
            'code': 'DATABASE_ERROR'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    # Return default response if no custom handling
    if response is not None:
        # Add error code to standard DRF responses
        if 'detail' in response.data:
            response.data = {
                'error': 'api_error',
                'message': response.data['detail'],
                'code': 'API_ERROR'
            }
    
    return response


def handle_empty_word_list_error():
    """Handle empty word list scenarios"""
    return {
        'error': 'empty_word_list',
        'message': 'No words available for your level. Please contact support.',
        'code': 'EMPTY_WORD_LIST',
        'suggestions': [
            'Try changing your Tamil level in settings',
            'Contact support to add more words'
        ]
    }


def handle_incomplete_profile_error(missing_fields):
    """Handle incomplete user profile scenarios"""
    return {
        'error': 'incomplete_profile',
        'message': 'Please complete your profile to continue.',
        'code': 'INCOMPLETE_PROFILE',
        'missing_fields': missing_fields,
        'action_required': 'complete_profile'
    }


def handle_network_failure_error():
    """Handle network failure scenarios"""
    return {
        'error': 'network_failure',
        'message': 'Network connection failed. Please check your internet connection.',
        'code': 'NETWORK_FAILURE',
        'retry_after': 30,
        'offline_mode_available': True
    }


def handle_partial_quiz_error(session_id):
    """Handle partial quiz submission errors"""
    return {
        'error': 'partial_quiz_submission',
        'message': 'Quiz was partially completed. Your progress has been saved.',
        'code': 'PARTIAL_QUIZ',
        'session_id': session_id,
        'action_available': 'resume_quiz'
    }


def handle_race_condition_error():
    """Handle race condition errors"""
    return {
        'error': 'concurrent_modification',
        'message': 'Data was modified by another request. Please refresh and try again.',
        'code': 'RACE_CONDITION',
        'action_required': 'refresh_data'
    }


def handle_audio_unavailable_error():
    """Handle audio unavailable scenarios"""
    return {
        'error': 'audio_unavailable',
        'message': 'Audio not available for this word. Text-to-speech will be used.',
        'code': 'AUDIO_UNAVAILABLE',
        'fallback': 'tts_available'
    }


def handle_session_expired_error():
    """Handle expired session scenarios"""
    return {
        'error': 'session_expired',
        'message': 'Your session has expired. Please log in again.',
        'code': 'SESSION_EXPIRED',
        'action_required': 'login_required'
    }


def handle_duplicate_question_error():
    """Handle duplicate question scenarios"""
    return {
        'error': 'duplicate_questions',
        'message': 'Not enough unique questions available. Some questions may repeat.',
        'code': 'DUPLICATE_QUESTIONS',
        'warning': True
    }
