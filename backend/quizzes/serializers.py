from rest_framework import serializers
from .models import QuizSession, QuizQuestion
from vocabulary.serializers import WordSerializer


class QuizQuestionSerializer(serializers.ModelSerializer):
    word = WordSerializer(read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = ('id', 'word', 'question_type', 'question_text', 
                 'answer_options', 'is_correct', 'response_time_seconds',
                 'asked_at')
        read_only_fields = ('id', 'is_correct', 'asked_at')


class QuizSessionSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    accuracy_percentage = serializers.ReadOnlyField()
    duration_minutes = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = QuizSession
        fields = ('id', 'quiz_type', 'total_questions', 'correct_answers',
                 'accuracy_percentage', 'duration_minutes', 'xp_earned',
                 'started_at', 'completed_at', 'is_completed', 'questions')
        read_only_fields = ('id', 'correct_answers', 'xp_earned', 
                           'started_at', 'completed_at')


class StartQuizSerializer(serializers.Serializer):
    quiz_type = serializers.ChoiceField(choices=QuizSession.QUIZ_TYPES, default='daily')
    word_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=20
    )
    question_types = serializers.ListField(
        child=serializers.ChoiceField(choices=QuizQuestion.QUESTION_TYPES),
        required=False,
        default=['mcq', 'fill_blank', 'audio']
    )


class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    user_answer = serializers.CharField(max_length=500)
    response_time = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)


class QuizSummarySerializer(serializers.Serializer):
    session_summary = serializers.DictField()
    word_progress_updates = serializers.ListField()
    new_achievements = serializers.ListField()
