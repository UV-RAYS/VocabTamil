from rest_framework import serializers
from .models import Word, UserWordProgress, WordList, WordListItem
from django.contrib.auth import get_user_model

User = get_user_model()


class WordSerializer(serializers.ModelSerializer):
    audio_url = serializers.ReadOnlyField()
    primary_meaning = serializers.ReadOnlyField()
    
    class Meta:
        model = Word
        fields = ('id', 'tamil_word', 'transliteration', 'meanings',
                 'example_tamil', 'example_english', 'audio_url',
                 'has_native_audio', 'category', 'difficulty_level',
                 'frequency_rank', 'primary_meaning')


class UserWordProgressSerializer(serializers.ModelSerializer):
    accuracy_percentage = serializers.ReadOnlyField()
    is_due_for_review = serializers.ReadOnlyField()
    
    class Meta:
        model = UserWordProgress
        fields = ('mastery_level', 'times_seen', 'times_correct',
                 'times_incorrect', 'next_review_date', 'accuracy_percentage',
                 'is_due_for_review', 'average_response_time', 'last_reviewed_at')
        read_only_fields = ('times_seen', 'times_correct', 'times_incorrect',
                           'next_review_date', 'last_reviewed_at')


class WordWithProgressSerializer(serializers.ModelSerializer):
    audio_url = serializers.ReadOnlyField()
    primary_meaning = serializers.ReadOnlyField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Word
        fields = ('id', 'tamil_word', 'transliteration', 'meanings',
                 'example_tamil', 'example_english', 'audio_url',
                 'has_native_audio', 'category', 'difficulty_level',
                 'primary_meaning', 'user_progress')
    
    def get_user_progress(self, obj):
        user = self.context.get('user')
        if not user or not user.is_authenticated:
            return None
        
        try:
            progress = UserWordProgress.objects.get(user=user, word=obj)
            return {
                'mastery_level': progress.mastery_level,
                'times_seen': progress.times_seen,
                'times_correct': progress.times_correct,
                'accuracy_percentage': progress.accuracy_percentage,
                'is_due_for_review': progress.is_due_for_review,
                'is_new': progress.times_seen == 0
            }
        except UserWordProgress.DoesNotExist:
            return {
                'mastery_level': 0,
                'times_seen': 0,
                'times_correct': 0,
                'accuracy_percentage': 0,
                'is_due_for_review': False,
                'is_new': True
            }


class WordListSerializer(serializers.ModelSerializer):
    word_count = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = WordList
        fields = ('id', 'name', 'description', 'category', 'is_public',
                 'word_count', 'created_by_name', 'created_at')
        read_only_fields = ('created_by', 'created_at')


class WordListDetailSerializer(serializers.ModelSerializer):
    words = WordWithProgressSerializer(many=True, read_only=True)
    word_count = serializers.ReadOnlyField()
    
    class Meta:
        model = WordList
        fields = ('id', 'name', 'description', 'category', 'is_public',
                 'words', 'word_count', 'created_at')
        read_only_fields = ('created_by', 'created_at')
