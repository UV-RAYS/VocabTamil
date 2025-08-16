from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    """Custom User model with Tamil learning specific fields"""
    
    TAMIL_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    UI_LANGUAGES = [
        ('en', 'English'),
        ('ta', 'Tamil'),
    ]
    
    # Profile & Settings
    tamil_level = models.CharField(
        max_length=20, 
        choices=TAMIL_LEVELS, 
        default='beginner'
    )
    daily_word_goal = models.PositiveIntegerField(default=10)
    ui_language = models.CharField(
        max_length=10, 
        choices=UI_LANGUAGES, 
        default='en'
    )
    
    # Gamification
    total_xp = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username
    
    def update_streak(self):
        """Update user's streak based on activity"""
        today = timezone.now().date()
        
        if self.last_activity_date is None:
            # First activity
            self.current_streak = 1
            self.longest_streak = max(self.longest_streak, 1)
        elif self.last_activity_date == today:
            # Already active today, no change
            return
        elif self.last_activity_date == today - timezone.timedelta(days=1):
            # Consecutive day
            self.current_streak += 1
            self.longest_streak = max(self.longest_streak, self.current_streak)
        else:
            # Streak broken
            self.current_streak = 1
        
        self.last_activity_date = today
        self.save(update_fields=['current_streak', 'longest_streak', 'last_activity_date'])
    
    def add_xp(self, points):
        """Add XP points to user"""
        self.total_xp += points
        self.save(update_fields=['total_xp'])
        return self.total_xp
    
    @property
    def words_learned_count(self):
        """Get count of words user has learned"""
        return self.word_progress.filter(mastery_level__gte=1).count()
    
    @property
    def words_mastered_count(self):
        """Get count of words user has mastered"""
        return self.word_progress.filter(mastery_level=3).count()
    
    @property
    def average_accuracy(self):
        """Calculate user's overall accuracy percentage"""
        progress = self.word_progress.exclude(times_seen=0)
        if not progress.exists():
            return 0.0
        
        total_correct = sum(p.times_correct for p in progress)
        total_attempts = sum(p.times_seen for p in progress)
        
        return (total_correct / total_attempts * 100) if total_attempts > 0 else 0.0
