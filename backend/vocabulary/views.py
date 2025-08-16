from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Word, UserWordProgress, WordList
from .serializers import (
    WordSerializer, 
    WordWithProgressSerializer, 
    UserWordProgressSerializer,
    WordListSerializer,
    WordListDetailSerializer
)
from .services import WordLearningService


class DailyWordsView(generics.ListAPIView):
    """Get daily words for learning based on user's progress and SRS"""
    serializer_class = WordWithProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        limit = int(self.request.query_params.get('limit', user.daily_word_goal))
        
        service = WordLearningService(user)
        return service.get_daily_words(limit)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Count new vs review words
        new_words = sum(1 for word_data in serializer.data 
                       if word_data['user_progress']['is_new'])
        review_words = len(serializer.data) - new_words
        
        return Response({
            'words': serializer.data,
            'total_count': len(serializer.data),
            'new_words': new_words,
            'review_words': review_words
        })


class ReviewWordsView(generics.ListAPIView):
    """Get words that need review based on spaced repetition"""
    serializer_class = WordWithProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        service = WordLearningService(user)
        return service.get_review_words()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


class WeakWordsView(generics.ListAPIView):
    """Get words user struggles with"""
    serializer_class = WordWithProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        service = WordLearningService(user)
        return service.get_weak_words()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        weak_words = []
        for word_data in serializer.data:
            progress = word_data['user_progress']
            weak_words.append({
                'word': {
                    'id': word_data['id'],
                    'tamil_word': word_data['tamil_word'],
                    'transliteration': word_data['transliteration'],
                    'meanings': word_data['meanings']
                },
                'progress': {
                    'times_seen': progress['times_seen'],
                    'times_correct': progress['times_correct'],
                    'accuracy': progress['accuracy_percentage'],
                    'last_incorrect': None  # TODO: Add this field to model
                }
            })
        
        return Response({'weak_words': weak_words})


class WordSearchView(generics.ListAPIView):
    """Search words by Tamil text, transliteration, or meaning"""
    serializer_class = WordWithProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        category = self.request.query_params.get('category', '')
        
        queryset = Word.objects.all()
        
        if query:
            queryset = queryset.filter(
                Q(tamil_word__icontains=query) |
                Q(transliteration__icontains=query) |
                Q(meanings__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset[:20]  # Limit results

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'words': serializer.data,
            'total_count': len(serializer.data)
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_word_learned(request, word_id):
    """Mark a word as learned (seen in learning mode)"""
    try:
        word = Word.objects.get(id=word_id)
        user = request.user
        
        progress, created = UserWordProgress.objects.get_or_create(
            user=user, word=word
        )
        
        if created or progress.times_seen == 0:
            progress.times_seen = 1
            progress.mastery_level = 1
            progress.save()
        
        return Response({
            'success': True,
            'user_progress': {
                'mastery_level': progress.mastery_level,
                'times_seen': progress.times_seen
            }
        })
    
    except Word.DoesNotExist:
        return Response(
            {'error': 'Word not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


class WordListView(generics.ListCreateAPIView):
    """List and create word lists"""
    serializer_class = WordListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return WordList.objects.filter(
            Q(created_by=user) | Q(is_public=True)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WordListDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a word list"""
    serializer_class = WordListDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return WordList.objects.filter(
            Q(created_by=user) | Q(is_public=True)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
