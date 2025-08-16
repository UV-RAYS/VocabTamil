from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Achievement(models.Model):
    """Achievements that users can unlock"""
    
    CRITERIA_TYPES = [
        ('words_learned', 'Words Learned'),
        ('words_mastered', 'Words Mastered'),
        ('streak', 'Daily Streak'),
        ('xp', 'Total XP'),
        ('accuracy', 'Quiz Accuracy'),
        ('speed', 'Response Speed'),
        ('quiz_sessions', 'Quiz Sessions Completed'),
        ('category_mastery', 'Category Mastery'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Emoji or icon class")
    
    # Unlock Criteria
    criteria_type = models.CharField(max_length=30, choices=CRITERIA_TYPES)
    criteria_value = models.PositiveIntegerField()
    criteria_data = models.JSONField(default=dict, blank=True, help_text="Additional criteria parameters")
    
    # Rewards
    xp_reward = models.PositiveIntegerField(default=0)
    
    # Display
    badge_color = models.CharField(max_length=20, default='blue')
    is_hidden = models.BooleanField(default=False, help_text="Hidden until unlocked")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'achievements'
        ordering = ['criteria_value']
    
    def __str__(self):
        return self.name
    
    def check_unlock_for_user(self, user):
        """Check if user meets criteria for this achievement"""
        if self.user_achievements.filter(user=user).exists():
            return False  # Already unlocked
        
        if self.criteria_type == 'words_learned':
            return user.words_learned_count >= self.criteria_value
        
        elif self.criteria_type == 'words_mastered':
            return user.words_mastered_count >= self.criteria_value
        
        elif self.criteria_type == 'streak':
            return user.current_streak >= self.criteria_value
        
        elif self.criteria_type == 'xp':
            return user.total_xp >= self.criteria_value
        
        elif self.criteria_type == 'accuracy':
            return user.average_accuracy >= self.criteria_value
        
        elif self.criteria_type == 'quiz_sessions':
            return user.quiz_sessions.filter(completed_at__isnull=False).count() >= self.criteria_value
        
        elif self.criteria_type == 'category_mastery':
            # Check if user has mastered X words in a specific category
            category = self.criteria_data.get('category')
            if category:
                mastered_in_category = user.word_progress.filter(
                    word__category=category,
                    mastery_level=3
                ).count()
                return mastered_in_category >= self.criteria_value
        
        return False


class UserAchievement(models.Model):
    """Achievements earned by users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='user_achievements')
    
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_achievements'
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class LeaderboardEntry(models.Model):
    """Leaderboard entries for different time periods"""
    
    LEADERBOARD_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    leaderboard_type = models.CharField(max_length=20, choices=LEADERBOARD_TYPES)
    
    # Metrics
    xp_earned = models.PositiveIntegerField(default=0)
    words_learned = models.PositiveIntegerField(default=0)
    quiz_sessions = models.PositiveIntegerField(default=0)
    accuracy_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Ranking
    rank = models.PositiveIntegerField()
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaderboard_entries'
        unique_together = ['user', 'leaderboard_type', 'period_start']
        indexes = [
            models.Index(fields=['leaderboard_type', 'rank']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.leaderboard_type} #{self.rank}"


class Badge(models.Model):
    """Special badges for achievements and milestones"""
    
    BADGE_TYPES = [
        ('milestone', 'Milestone'),
        ('special', 'Special Event'),
        ('category', 'Category Master'),
        ('streak', 'Streak Achievement'),
        ('speed', 'Speed Achievement'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    
    # Visual
    icon = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='gold')
    
    # Requirements
    requirements = models.JSONField(help_text="Requirements to earn this badge")
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'badges'
    
    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """Badges earned by users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges')
    
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_badges'
        unique_together = ['user', 'badge']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class DailyChallenge(models.Model):
    """Daily challenges for users"""
    
    CHALLENGE_TYPES = [
        ('word_count', 'Learn X Words'),
        ('accuracy', 'Achieve X% Accuracy'),
        ('speed', 'Complete Quiz in X Minutes'),
        ('streak', 'Maintain Streak'),
        ('category', 'Master Category'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    
    # Challenge parameters
    target_value = models.PositiveIntegerField()
    challenge_data = models.JSONField(default=dict, blank=True)
    
    # Rewards
    xp_reward = models.PositiveIntegerField(default=50)
    badge_reward = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timing
    date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_challenges'
        unique_together = ['date', 'challenge_type']
    
    def __str__(self):
        return f"{self.date} - {self.name}"


class UserChallengeProgress(models.Model):
    """User progress on daily challenges"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge_progress')
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE, related_name='user_progress')
    
    # Progress
    current_value = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_challenge_progress'
        unique_together = ['user', 'challenge']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.name} ({self.current_value}/{self.challenge.target_value})"
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.challenge.target_value == 0:
            return 0
        return min(100, (self.current_value / self.challenge.target_value) * 100)
    
    def update_progress(self, increment=1):
        """Update challenge progress"""
        self.current_value += increment
        
        if self.current_value >= self.challenge.target_value and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            
            # Award rewards
            self.user.add_xp(self.challenge.xp_reward)
            
            if self.challenge.badge_reward:
                UserBadge.objects.get_or_create(
                    user=self.user,
                    badge=self.challenge.badge_reward
                )
        
        self.save()
