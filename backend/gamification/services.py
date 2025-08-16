from .models import Achievement, UserAchievement
from django.utils import timezone


class AchievementService:
    """Service for managing achievements and rewards"""
    
    def __init__(self, user):
        self.user = user
    
    def check_and_award_achievements(self):
        """Check all achievements and award any newly unlocked ones"""
        new_achievements = []
        
        # Get all achievements user hasn't earned yet
        earned_achievement_ids = UserAchievement.objects.filter(
            user=self.user
        ).values_list('achievement_id', flat=True)
        
        pending_achievements = Achievement.objects.exclude(
            id__in=earned_achievement_ids
        )
        
        for achievement in pending_achievements:
            if achievement.check_unlock_for_user(self.user):
                # Award the achievement
                user_achievement = UserAchievement.objects.create(
                    user=self.user,
                    achievement=achievement
                )
                
                # Award XP
                if achievement.xp_reward > 0:
                    self.user.add_xp(achievement.xp_reward)
                
                new_achievements.append({
                    'id': achievement.id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'icon': achievement.icon,
                    'xp_reward': achievement.xp_reward
                })
        
        return new_achievements
    
    def get_progress_towards_achievements(self):
        """Get user's progress towards unearned achievements"""
        earned_achievement_ids = UserAchievement.objects.filter(
            user=self.user
        ).values_list('achievement_id', flat=True)
        
        pending_achievements = Achievement.objects.exclude(
            id__in=earned_achievement_ids,
            is_hidden=True
        )
        
        progress_data = []
        for achievement in pending_achievements:
            current_value = self._get_current_value_for_achievement(achievement)
            progress_percentage = min(100, (current_value / achievement.criteria_value) * 100)
            
            progress_data.append({
                'achievement': {
                    'id': achievement.id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'icon': achievement.icon,
                    'xp_reward': achievement.xp_reward
                },
                'current_value': current_value,
                'target_value': achievement.criteria_value,
                'progress_percentage': progress_percentage
            })
        
        return sorted(progress_data, key=lambda x: x['progress_percentage'], reverse=True)
    
    def _get_current_value_for_achievement(self, achievement):
        """Get user's current value for achievement criteria"""
        if achievement.criteria_type == 'words_learned':
            return self.user.words_learned_count
        
        elif achievement.criteria_type == 'words_mastered':
            return self.user.words_mastered_count
        
        elif achievement.criteria_type == 'streak':
            return self.user.current_streak
        
        elif achievement.criteria_type == 'xp':
            return self.user.total_xp
        
        elif achievement.criteria_type == 'accuracy':
            return int(self.user.average_accuracy)
        
        elif achievement.criteria_type == 'quiz_sessions':
            return self.user.quiz_sessions.filter(completed_at__isnull=False).count()
        
        elif achievement.criteria_type == 'category_mastery':
            category = achievement.criteria_data.get('category')
            if category:
                return self.user.word_progress.filter(
                    word__category=category,
                    mastery_level=3
                ).count()
        
        return 0
