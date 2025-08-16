from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Achievement, UserAchievement
from .services import AchievementService


class AchievementListView(generics.ListAPIView):
    """List all achievements with user's earned status"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get all achievements
        all_achievements = Achievement.objects.all().order_by('criteria_value')
        
        # Get user's earned achievements
        earned_achievement_ids = set(
            UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)
        )
        
        achievements_data = []
        for achievement in all_achievements:
            is_earned = achievement.id in earned_achievement_ids
            
            # Don't show hidden achievements unless earned
            if achievement.is_hidden and not is_earned:
                continue
            
            achievements_data.append({
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'icon': achievement.icon,
                'criteria_type': achievement.criteria_type,
                'criteria_value': achievement.criteria_value,
                'xp_reward': achievement.xp_reward,
                'badge_color': achievement.badge_color,
                'is_earned': is_earned,
                'earned_at': None  # TODO: Add earned date if needed
            })
        
        return Response({'achievements': achievements_data})


class AchievementProgressView(generics.GenericAPIView):
    """Get user's progress towards unearned achievements"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        achievement_service = AchievementService(user)
        
        progress_data = achievement_service.get_progress_towards_achievements()
        
        return Response({'achievement_progress': progress_data})
