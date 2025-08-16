from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json

User = get_user_model()

class Word(models.Model):
    """Tamil word with meanings, examples, and metadata"""
    
    DIFFICULTY_LEVELS = [
        (1, 'Very Easy'),
        (2, 'Easy'),
        (3, 'Medium'),
        (4, 'Hard'),
        (5, 'Very Hard'),
    ]
    
    CATEGORIES = [
        ('emotions', 'Emotions'),
        ('nature', 'Nature'),
        ('food', 'Food & Cooking'),
        ('family', 'Family & Relationships'),
        ('education', 'Education'),
        ('work', 'Work & Career'),
        ('health', 'Health & Body'),
        ('travel', 'Travel & Places'),
        ('time', 'Time & Calendar'),
        ('numbers', 'Numbers & Math'),
        ('colors', 'Colors'),
        ('animals', 'Animals'),
        ('clothing', 'Clothing'),
        ('weather', 'Weather'),
        ('sports', 'Sports & Games'),
        ('technology', 'Technology'),
        ('culture', 'Culture & Traditions'),
        ('proverbs', 'Proverbs & Sayings'),
        ('grammar', 'Grammar Words'),
        ('exam', 'Exam Vocabulary'),
    ]
    
    # Core word data
    tamil_word = models.CharField(max_length=100, unique=True)
    transliteration = models.CharField(max_length=100)
    
    # Meanings stored as JSON array
    meanings = models.JSONField(help_text="Array of English meanings")
    
    # Examples
    example_tamil = models.TextField(blank=True)
    example_english = models.TextField(blank=True)
    
    # Audio
    audio_file = models.FileField(upload_to='audio/words/', blank=True, null=True)
    has_native_audio = models.BooleanField(default=False)
    
    # Categorization
    category = models.CharField(max_length=50, choices=CATEGORIES)
    difficulty_level = models.IntegerField(choices=DIFFICULTY_LEVELS, default=1)
    frequency_rank = models.PositiveIntegerField(null=True, blank=True, help_text="How common the word is (1=most common)")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'words'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['tamil_word']),
        ]
    
    def __str__(self):
        return f"{self.tamil_word} ({self.transliteration})"
    
    @property
    def audio_url(self):
        """Get audio file URL"""
        if self.audio_file:
            return self.audio_file.url
        return None
    
    @property
    def primary_meaning(self):
        """Get the first/primary meaning"""
        if isinstance(self.meanings, list) and self.meanings:
            return self.meanings[0]
        return ""


class UserWordProgress(models.Model):
    """Track user's progress with individual words"""
    
    MASTERY_LEVELS = [
        (0, 'New'),
        (1, 'Learning'),
        (2, 'Familiar'),
        (3, 'Mastered'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_progress')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='user_progress')
    
    # Learning Progress
    mastery_level = models.IntegerField(choices=MASTERY_LEVELS, default=0)
    times_seen = models.PositiveIntegerField(default=0)
    times_correct = models.PositiveIntegerField(default=0)
    times_incorrect = models.PositiveIntegerField(default=0)
    
    # Spaced Repetition System (SRS)
    next_review_date = models.DateField(default=timezone.now)
    review_interval_days = models.PositiveIntegerField(default=1)
    ease_factor = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('2.50'))
    
    # Performance Metrics
    average_response_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    last_response_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_reviewed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_word_progress'
        unique_together = ['user', 'word']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['next_review_date']),
            models.Index(fields=['mastery_level']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.word.tamil_word} (Level {self.mastery_level})"
    
    @property
    def accuracy_percentage(self):
        """Calculate accuracy percentage for this word"""
        if self.times_seen == 0:
            return 0.0
        return (self.times_correct / self.times_seen) * 100
    
    @property
    def is_due_for_review(self):
        """Check if word is due for review"""
        return timezone.now().date() >= self.next_review_date
    
    def update_srs(self, is_correct, response_time=None):
        """Update spaced repetition parameters based on answer"""
        self.times_seen += 1
        
        if response_time:
            if self.average_response_time:
                # Update running average
                self.average_response_time = (self.average_response_time + Decimal(str(response_time))) / 2
            else:
                self.average_response_time = Decimal(str(response_time))
            self.last_response_time = Decimal(str(response_time))
        
        if is_correct:
            self.times_correct += 1
            
            # Increase interval based on ease factor
            if self.review_interval_days == 1:
                self.review_interval_days = 3
            else:
                self.review_interval_days = int(self.review_interval_days * float(self.ease_factor))
            
            # Increase ease factor slightly for correct answers
            self.ease_factor = min(Decimal('3.00'), self.ease_factor + Decimal('0.10'))
            
            # Update mastery level
            if self.mastery_level < 3:
                if self.times_correct >= 3 and self.accuracy_percentage >= 80:
                    self.mastery_level += 1
        else:
            self.times_incorrect += 1
            
            # Reset interval for incorrect answers
            self.review_interval_days = 1
            
            # Decrease ease factor for incorrect answers
            self.ease_factor = max(Decimal('1.30'), self.ease_factor - Decimal('0.20'))
            
            # Potentially decrease mastery level for very poor performance
            if self.accuracy_percentage < 50 and self.mastery_level > 0:
                self.mastery_level = max(0, self.mastery_level - 1)
        
        # Set next review date
        self.next_review_date = timezone.now().date() + timezone.timedelta(days=self.review_interval_days)
        self.last_reviewed_at = timezone.now()
        
        self.save()


class WordList(models.Model):
    """Custom word lists created by teachers or users"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_word_lists')
    
    # List Properties
    is_public = models.BooleanField(default=False)
    category = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'word_lists'
    
    def __str__(self):
        return self.name
    
    @property
    def word_count(self):
        """Get number of words in this list"""
        return self.words.count()


class WordListItem(models.Model):
    """Individual words within a word list"""
    
    word_list = models.ForeignKey(WordList, on_delete=models.CASCADE, related_name='items')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='list_items')
    order_index = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'word_list_items'
        unique_together = ['word_list', 'word']
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.word_list.name} - {self.word.tamil_word}"
