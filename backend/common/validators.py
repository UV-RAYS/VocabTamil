"""
Custom validators for input sanitization and validation
"""
import re
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _


def sanitize_text_input(value):
    """Sanitize text input to prevent XSS and injection attacks"""
    if not value:
        return value
    
    # Strip HTML tags
    cleaned = strip_tags(str(value))
    
    # Remove potentially dangerous characters
    cleaned = re.sub(r'[<>"\'\&\$\{\}]', '', cleaned)
    
    # Limit length
    if len(cleaned) > 1000:
        raise ValidationError(_('Input too long. Maximum 1000 characters allowed.'))
    
    return cleaned.strip()


def validate_tamil_text(value):
    """Validate Tamil text input"""
    if not value:
        return
    
    # Allow Tamil unicode range, English letters, numbers, and common punctuation
    tamil_pattern = r'^[\u0B80-\u0BFF\u0020-\u007Ea-zA-Z0-9\s\.,!?\-\(\)]+$'
    
    if not re.match(tamil_pattern, value):
        raise ValidationError(_('Invalid characters in Tamil text.'))
    
    if len(value) > 200:
        raise ValidationError(_('Tamil text too long. Maximum 200 characters allowed.'))


def validate_quiz_answer(value):
    """Validate quiz answer input"""
    if not value:
        return
    
    # Sanitize and validate
    cleaned = sanitize_text_input(value)
    
    # Additional quiz-specific validation
    if len(cleaned) > 500:
        raise ValidationError(_('Answer too long. Maximum 500 characters allowed.'))
    
    return cleaned


def validate_xp_amount(value):
    """Validate XP amounts to prevent manipulation"""
    if value < 0:
        raise ValidationError(_('XP cannot be negative.'))
    
    if value > 10000:  # Reasonable daily limit
        raise ValidationError(_('XP amount too high. Maximum 10000 per action.'))
    
    return value


def validate_response_time(value):
    """Validate quiz response time"""
    if value is None:
        return value
    
    if value < 0:
        raise ValidationError(_('Response time cannot be negative.'))
    
    if value > 3600:  # 1 hour max
        raise ValidationError(_('Response time too high. Maximum 1 hour allowed.'))
    
    return value


def validate_word_list_size(word_ids):
    """Validate word list size for quizzes"""
    if not word_ids:
        raise ValidationError(_('Word list cannot be empty.'))
    
    if len(word_ids) > 50:
        raise ValidationError(_('Too many words. Maximum 50 words per quiz.'))
    
    # Check for duplicates
    if len(word_ids) != len(set(word_ids)):
        raise ValidationError(_('Duplicate words not allowed in quiz.'))
    
    return word_ids


def validate_daily_goal(value):
    """Validate daily word learning goal"""
    if value < 1:
        raise ValidationError(_('Daily goal must be at least 1 word.'))
    
    if value > 100:
        raise ValidationError(_('Daily goal too high. Maximum 100 words per day.'))
    
    return value
