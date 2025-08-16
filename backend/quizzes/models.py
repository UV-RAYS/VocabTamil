from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from vocabulary.models import Word
import json

User = get_user_model()

class QuizSession(models.Model):
    """A quiz session containing multiple questions"""
    
    QUIZ_TYPES = [
        ('daily', 'Daily Practice'),
        ('review', 'Review Session'),
        ('speed', 'Speed Round'),
        ('custom', 'Custom Quiz'),
        ('placement', 'Placement Test'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_sessions')
    
    # Session Details
    quiz_type = models.CharField(max_length=30, choices=QUIZ_TYPES)
    total_questions = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField(default=0)
    
    # Performance
    total_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    xp_earned = models.PositiveIntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Session metadata (JSON)
    session_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'quiz_sessions'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz_type} ({self.started_at.date()})"
    
    @property
    def is_completed(self):
        """Check if quiz session is completed"""
        return self.completed_at is not None
    
    @property
    def accuracy_percentage(self):
        """Calculate accuracy percentage"""
        if self.total_questions == 0:
            return 0.0
        return (self.correct_answers / self.total_questions) * 100
    
    @property
    def duration_minutes(self):
        """Get session duration in minutes"""
        if self.total_time_seconds:
            return round(self.total_time_seconds / 60, 1)
        return 0.0
    
    def complete_session(self):
        """Mark session as completed and calculate final stats"""
        if self.is_completed:
            return
        
        self.completed_at = timezone.now()
        
        # Calculate total time if not set
        if not self.total_time_seconds:
            duration = self.completed_at - self.started_at
            self.total_time_seconds = int(duration.total_seconds())
        
        # Calculate XP earned
        base_xp = self.correct_answers * 10
        accuracy_bonus = int(self.accuracy_percentage / 10) * 5  # 5 XP per 10% accuracy
        speed_bonus = max(0, 50 - self.duration_minutes) if self.duration_minutes > 0 else 0
        
        self.xp_earned = base_xp + accuracy_bonus + int(speed_bonus)
        
        # Add XP to user
        self.user.add_xp(self.xp_earned)
        
        # Update user streak
        self.user.update_streak()
        
        self.save()


class QuizQuestion(models.Model):
    """Individual question within a quiz session"""
    
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('fill_blank', 'Fill in the Blank'),
        ('match', 'Match Pairs'),
        ('audio', 'Audio Recognition'),
        ('typing', 'Type Translation'),
    ]
    
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='questions')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='quiz_questions')
    
    # Question Details
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPES)
    question_text = models.TextField()
    correct_answer = models.TextField()
    user_answer = models.TextField(blank=True)
    
    # Options for MCQ (JSON array)
    answer_options = models.JSONField(null=True, blank=True)
    
    # Performance
    is_correct = models.BooleanField(null=True, blank=True)
    response_time_seconds = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    asked_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'quiz_questions'
        ordering = ['asked_at']
    
    def __str__(self):
        return f"Q: {self.question_text[:50]}..."
    
    def submit_answer(self, user_answer, response_time=None):
        """Submit and evaluate user's answer"""
        self.user_answer = user_answer
        self.answered_at = timezone.now()
        
        if response_time:
            self.response_time_seconds = response_time
        
        # Evaluate answer
        self.is_correct = self._evaluate_answer(user_answer)
        
        # Update session stats
        if self.is_correct:
            self.session.correct_answers += 1
            self.session.save(update_fields=['correct_answers'])
        
        # Update user's word progress
        from vocabulary.models import UserWordProgress
        progress, created = UserWordProgress.objects.get_or_create(
            user=self.session.user,
            word=self.word
        )
        progress.update_srs(self.is_correct, float(response_time) if response_time else None)
        
        self.save()
        return self.is_correct
    
    def _evaluate_answer(self, user_answer):
        """Evaluate if user's answer is correct"""
        if not user_answer:
            return False
        
        user_answer = user_answer.strip().lower()
        correct_answer = self.correct_answer.strip().lower()
        
        if self.question_type == 'mcq':
            return user_answer == correct_answer
        
        elif self.question_type == 'fill_blank':
            # Allow for minor variations in spelling
            return user_answer == correct_answer or user_answer in correct_answer
        
        elif self.question_type == 'typing':
            # More lenient matching for typing questions
            return (user_answer == correct_answer or 
                    user_answer in correct_answer or 
                    correct_answer in user_answer)
        
        elif self.question_type == 'audio':
            return user_answer == correct_answer
        
        elif self.question_type == 'match':
            return user_answer == correct_answer
        
        return False


class QuizTemplate(models.Model):
    """Template for generating quiz questions"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Question generation rules
    question_types = models.JSONField(help_text="Array of question types to include")
    difficulty_range = models.JSONField(help_text="Min and max difficulty levels [min, max]")
    categories = models.JSONField(help_text="Array of word categories to include")
    
    # Quiz parameters
    total_questions = models.PositiveIntegerField(default=10)
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_templates')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quiz_templates'
    
    def __str__(self):
        return self.name
    
    def generate_questions(self, user):
        """Generate quiz questions based on template rules"""
        from .services import QuizGeneratorService
        generator = QuizGeneratorService(user)
        return generator.generate_from_template(self)
