from django.db.models import Q
from django.utils import timezone
from .models import Word, UserWordProgress
import random


class WordLearningService:
    """Service for managing word learning logic and spaced repetition"""
    
    def __init__(self, user):
        self.user = user
    
    def get_daily_words(self, limit=10):
        """Get daily words for learning based on SRS and user level"""
        # Get words due for review
        review_words = list(self.get_review_words())
        
        # Calculate how many new words to add
        review_count = len(review_words)
        new_words_needed = max(0, limit - review_count)
        
        # Get new words based on user's Tamil level
        new_words = list(self.get_new_words(new_words_needed))
        
        # Combine and shuffle
        all_words = review_words + new_words
        random.shuffle(all_words)
        
        return all_words[:limit]
    
    def get_review_words(self):
        """Get words that are due for review based on SRS"""
        today = timezone.now().date()
        
        return Word.objects.filter(
            user_progress__user=self.user,
            user_progress__next_review_date__lte=today,
            user_progress__mastery_level__lt=3  # Not fully mastered
        ).select_related().order_by('user_progress__next_review_date')
    
    def get_new_words(self, limit=5):
        """Get new words user hasn't seen yet"""
        # Get words user hasn't encountered
        seen_word_ids = UserWordProgress.objects.filter(
            user=self.user
        ).values_list('word_id', flat=True)
        
        # Filter by user's Tamil level
        difficulty_map = {
            'beginner': [1, 2],
            'intermediate': [2, 3, 4],
            'advanced': [3, 4, 5]
        }
        
        allowed_difficulties = difficulty_map.get(self.user.tamil_level, [1, 2])
        
        return Word.objects.exclude(
            id__in=seen_word_ids
        ).filter(
            difficulty_level__in=allowed_difficulties
        ).order_by('frequency_rank', '?')[:limit]
    
    def get_weak_words(self, limit=20):
        """Get words user struggles with (low accuracy)"""
        return Word.objects.filter(
            user_progress__user=self.user,
            user_progress__times_seen__gte=3,  # Seen at least 3 times
            user_progress__times_correct__lt=2  # But correct less than 2 times
        ).select_related('user_progress').order_by(
            'user_progress__accuracy_percentage'
        )[:limit]
    
    def get_mastery_breakdown(self):
        """Get breakdown of words by mastery level"""
        progress_qs = UserWordProgress.objects.filter(user=self.user)
        
        breakdown = {
            'new': 0,
            'learning': 0,
            'familiar': 0,
            'mastered': 0
        }
        
        for progress in progress_qs:
            if progress.mastery_level == 0:
                breakdown['new'] += 1
            elif progress.mastery_level == 1:
                breakdown['learning'] += 1
            elif progress.mastery_level == 2:
                breakdown['familiar'] += 1
            elif progress.mastery_level == 3:
                breakdown['mastered'] += 1
        
        # Add words never seen
        total_words = Word.objects.count()
        seen_words = progress_qs.count()
        breakdown['new'] += max(0, total_words - seen_words)
        
        return breakdown
    
    def get_category_progress(self):
        """Get learning progress by category"""
        from django.db.models import Count, Avg
        
        categories = Word.objects.values('category').annotate(
            total_words=Count('id')
        )
        
        progress_data = []
        for category_data in categories:
            category = category_data['category']
            total_words = category_data['total_words']
            
            # Get user's progress in this category
            learned_count = UserWordProgress.objects.filter(
                user=self.user,
                word__category=category,
                mastery_level__gte=1
            ).count()
            
            mastery_rate = (learned_count / total_words * 100) if total_words > 0 else 0
            
            progress_data.append({
                'category': category,
                'words_learned': learned_count,
                'total_words': total_words,
                'mastery_rate': round(mastery_rate, 1)
            })
        
        return sorted(progress_data, key=lambda x: x['mastery_rate'], reverse=True)
