"""
Utility functions for handling race conditions and concurrent operations
"""
import logging
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from functools import wraps
from time import sleep
import random

logger = logging.getLogger(__name__)


def atomic_update_with_retry(max_retries=3, delay_range=(0.1, 0.5)):
    """
    Decorator to handle race conditions in database updates with retry logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    with transaction.atomic():
                        return func(*args, **kwargs)
                except IntegrityError as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Max retries exceeded for {func.__name__}: {str(e)}")
                        raise
                    
                    # Random delay to avoid thundering herd
                    delay = random.uniform(*delay_range)
                    sleep(delay)
                    logger.warning(f"Retry {attempt + 1} for {func.__name__} after IntegrityError")
                    
            return None
        return wrapper
    return decorator


def safe_user_progress_update(user, word, is_correct, response_time=None):
    """
    Safely update user progress with race condition handling
    """
    @atomic_update_with_retry()
    def _update_progress():
        from vocabulary.models import UserWordProgress
        
        # Use select_for_update to prevent race conditions
        try:
            progress = UserWordProgress.objects.select_for_update().get(
                user=user, word=word
            )
        except UserWordProgress.DoesNotExist:
            progress = UserWordProgress.objects.create(
                user=user, word=word
            )
        
        # Update progress
        progress.update_srs(is_correct, response_time)
        return progress
    
    return _update_progress()


def safe_xp_update(user, xp_amount):
    """
    Safely update user XP with race condition handling
    """
    @atomic_update_with_retry()
    def _update_xp():
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Use select_for_update to prevent race conditions
        user_obj = User.objects.select_for_update().get(id=user.id)
        user_obj.total_xp += xp_amount
        user_obj.save(update_fields=['total_xp'])
        return user_obj.total_xp
    
    return _update_xp()


def safe_streak_update(user):
    """
    Safely update user streak with race condition handling
    """
    @atomic_update_with_retry()
    def _update_streak():
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Use select_for_update to prevent race conditions
        user_obj = User.objects.select_for_update().get(id=user.id)
        user_obj.update_streak()
        return user_obj.current_streak
    
    return _update_streak()


def safe_achievement_check(user):
    """
    Safely check and award achievements with race condition handling
    """
    @atomic_update_with_retry()
    def _check_achievements():
        from gamification.services import AchievementService
        
        service = AchievementService(user)
        return service.check_and_award_achievements()
    
    return _check_achievements()


def handle_partial_quiz_submission(session_id, user):
    """
    Handle partial quiz submissions gracefully
    """
    try:
        from quizzes.models import QuizSession
        
        session = QuizSession.objects.get(id=session_id, user=user)
        
        # Check if session is already completed
        if session.is_completed:
            return {'status': 'already_completed', 'session': session}
        
        # Count answered questions
        answered_questions = session.questions.filter(
            answered_at__isnull=False
        ).count()
        
        if answered_questions == 0:
            # No questions answered, mark as abandoned
            session.delete()
            return {'status': 'abandoned'}
        
        # Partial completion - calculate partial results
        session.correct_answers = session.questions.filter(
            is_correct=True
        ).count()
        
        session.total_questions = answered_questions
        session.complete_session()
        
        return {'status': 'partial_completion', 'session': session}
        
    except ObjectDoesNotExist:
        return {'status': 'not_found'}
    except Exception as e:
        logger.error(f"Error handling partial quiz submission: {str(e)}")
        return {'status': 'error', 'message': str(e)}


def validate_session_ownership(session_id, user):
    """
    Validate that user owns the quiz session
    """
    try:
        from quizzes.models import QuizSession
        session = QuizSession.objects.get(id=session_id, user=user)
        return session
    except ObjectDoesNotExist:
        return None


def prevent_duplicate_questions(user, word_ids, recent_days=7):
    """
    Prevent duplicate questions in recent quizzes
    """
    from django.utils import timezone
    from datetime import timedelta
    from quizzes.models import QuizSession, QuizQuestion
    
    # Get recent quiz questions
    cutoff_date = timezone.now() - timedelta(days=recent_days)
    
    recent_word_ids = set(
        QuizQuestion.objects.filter(
            session__user=user,
            session__started_at__gte=cutoff_date
        ).values_list('word_id', flat=True)
    )
    
    # Filter out recently used words
    filtered_word_ids = [
        word_id for word_id in word_ids 
        if word_id not in recent_word_ids
    ]
    
    # If we filtered out too many, add some back
    if len(filtered_word_ids) < len(word_ids) * 0.5:
        # Add back some recent words if we don't have enough variety
        needed = min(len(word_ids) - len(filtered_word_ids), len(recent_word_ids))
        filtered_word_ids.extend(list(recent_word_ids)[:needed])
    
    return filtered_word_ids[:len(word_ids)]


def handle_network_timeout():
    """
    Handle network timeout scenarios
    """
    return {
        'error': 'network_timeout',
        'message': 'Request timed out. Please check your connection and try again.',
        'retry_after': 30
    }


def handle_empty_word_list(user):
    """
    Handle empty word list scenarios
    """
    from vocabulary.models import Word
    
    # Get basic words for the user's level
    difficulty_map = {
        'beginner': [1, 2],
        'intermediate': [2, 3, 4],
        'advanced': [3, 4, 5]
    }
    
    allowed_difficulties = difficulty_map.get(user.tamil_level, [1, 2])
    
    fallback_words = Word.objects.filter(
        difficulty_level__in=allowed_difficulties
    ).order_by('frequency_rank')[:5]
    
    if not fallback_words.exists():
        # Ultimate fallback - any words
        fallback_words = Word.objects.all()[:5]
    
    return list(fallback_words)
