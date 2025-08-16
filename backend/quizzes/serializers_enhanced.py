from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import QuizSession, QuizQuestion
from vocabulary.serializers import WordSerializer
from common.validators import (
    sanitize_text_input, 
    validate_quiz_answer, 
    validate_response_time,
    validate_word_list_size
)


class EnhancedQuizQuestionSerializer(serializers.ModelSerializer):
    word = WordSerializer(read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = ('id', 'word', 'question_type', 'question_text', 
                 'answer_options', 'is_correct', 'response_time_seconds',
                 'asked_at')
        read_only_fields = ('id', 'is_correct', 'asked_at')


class EnhancedQuizSessionSerializer(serializers.ModelSerializer):
    questions = EnhancedQuizQuestionSerializer(many=True, read_only=True)
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


class EnhancedStartQuizSerializer(serializers.Serializer):
    quiz_type = serializers.ChoiceField(choices=QuizSession.QUIZ_TYPES, default='daily')
    word_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1,
        max_length=50,
        allow_empty=False
    )
    question_types = serializers.ListField(
        child=serializers.ChoiceField(choices=QuizQuestion.QUESTION_TYPES),
        required=False,
        default=['mcq', 'fill_blank', 'audio'],
        max_length=5
    )

    def validate_word_ids(self, value):
        """Validate word IDs list"""
        try:
            return validate_word_list_size(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_question_types(self, value):
        """Validate question types"""
        if not value:
            return ['mcq', 'fill_blank', 'audio']
        
        # Ensure no duplicates
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate question types not allowed.")
        
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        word_ids = attrs.get('word_ids', [])
        question_types = attrs.get('question_types', [])
        
        # Ensure we have enough words for the quiz
        if len(word_ids) < len(question_types):
            raise serializers.ValidationError(
                "Not enough words for the selected question types."
            )
        
        return attrs


class EnhancedSubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(min_value=1)
    user_answer = serializers.CharField(
        max_length=500, 
        allow_blank=False,
        trim_whitespace=True
    )
    response_time = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False,
        min_value=0,
        max_value=3600
    )

    def validate_user_answer(self, value):
        """Validate and sanitize user answer"""
        try:
            return validate_quiz_answer(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_response_time(self, value):
        """Validate response time"""
        try:
            return validate_response_time(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_question_id(self, value):
        """Validate question ID exists"""
        if not QuizQuestion.objects.filter(id=value).exists():
            raise serializers.ValidationError("Question not found.")
        return value


class SafeQuizSummarySerializer(serializers.Serializer):
    session_summary = serializers.DictField()
    word_progress_updates = serializers.ListField()
    new_achievements = serializers.ListField()

    def validate_session_summary(self, value):
        """Validate session summary data"""
        required_fields = ['total_questions', 'correct_answers', 'accuracy', 'xp_earned']
        
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")
        
        # Validate numeric fields
        if value.get('total_questions', 0) < 0:
            raise serializers.ValidationError("Total questions cannot be negative.")
        
        if value.get('correct_answers', 0) < 0:
            raise serializers.ValidationError("Correct answers cannot be negative.")
        
        if value.get('accuracy', 0) < 0 or value.get('accuracy', 0) > 100:
            raise serializers.ValidationError("Accuracy must be between 0 and 100.")
        
        if value.get('xp_earned', 0) < 0:
            raise serializers.ValidationError("XP earned cannot be negative.")
        
        return value
