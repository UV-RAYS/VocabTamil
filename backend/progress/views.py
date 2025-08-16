from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum
from vocabulary.services import WordLearningService
from gamification.services import AchievementService


class DashboardView(generics.GenericAPIView):
    """Get comprehensive progress dashboard data"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        word_service = WordLearningService(user)
        achievement_service = AchievementService(user)
        
        # Daily progress
        daily_progress = {
            'words_learned_today': 0,  # TODO: Track daily activity
            'daily_goal': user.daily_word_goal,
            'progress_percentage': 0,  # TODO: Calculate based on today's activity
            'streak_count': user.current_streak,
            'xp_earned_today': 0  # TODO: Track daily XP
        }
        
        # Weekly stats
        quiz_sessions = user.quiz_sessions.filter(completed_at__isnull=False)
        total_time = quiz_sessions.aggregate(total=Sum('total_time_seconds'))['total'] or 0
        
        weekly_stats = {
            'words_learned': user.words_learned_count,
            'quiz_sessions': quiz_sessions.count(),
            'total_xp': user.total_xp,
            'average_accuracy': user.average_accuracy
        }
        
        # Mastery breakdown
        mastery_breakdown = word_service.get_mastery_breakdown()
        
        # Category progress
        category_progress = word_service.get_category_progress()
        
        return Response({
            'daily_progress': daily_progress,
            'weekly_stats': weekly_stats,
            'mastery_breakdown': mastery_breakdown,
            'category_progress': category_progress
        })


class LeaderboardView(generics.GenericAPIView):
    """Get leaderboard data"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        leaderboard_type = request.query_params.get('type', 'daily')
        limit = int(request.query_params.get('limit', 50))
        
        # For MVP, we'll use simple XP-based leaderboard
        from accounts.models import User
        
        if leaderboard_type == 'daily':
            # TODO: Implement daily XP tracking
            users = User.objects.filter(total_xp__gt=0).order_by('-total_xp')[:limit]
        else:
            users = User.objects.filter(total_xp__gt=0).order_by('-total_xp')[:limit]
        
        leaderboard_data = []
        for rank, user in enumerate(users, 1):
            leaderboard_data.append({
                'rank': rank,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name
                },
                'xp_today' if leaderboard_type == 'daily' else 'total_xp': user.total_xp,
                'words_learned_today' if leaderboard_type == 'daily' else 'words_learned': user.words_learned_count
            })
        
        # Find current user's rank
        current_user_rank = None
        current_user_xp = request.user.total_xp
        
        for entry in leaderboard_data:
            if entry['user']['id'] == request.user.id:
                current_user_rank = entry['rank']
                break
        
        return Response({
            'leaderboard': leaderboard_data,
            'current_user_rank': current_user_rank,
            'current_user_xp': current_user_xp
        })
