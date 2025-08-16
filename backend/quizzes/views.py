from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import QuizSession, QuizQuestion
from .serializers import (
    QuizSessionSerializer,
    QuizQuestionSerializer,
    StartQuizSerializer,
    SubmitAnswerSerializer,
    QuizSummarySerializer
)
from .services import QuizGeneratorService
from gamification.services import AchievementService


class StartQuizView(generics.CreateAPIView):
    """Start a new quiz session"""
    serializer_class = StartQuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        word_ids = serializer.validated_data['word_ids']
        quiz_type = serializer.validated_data['quiz_type']
        question_types = serializer.validated_data['question_types']
        
        # Generate quiz
        generator = QuizGeneratorService(user)
        session, questions = generator.generate_daily_quiz(word_ids, question_types)
        
        # Serialize questions for response
        question_data = []
        for question in questions:
            data = {
                'id': question.id,
                'word_id': question.word.id,
                'question_type': question.question_type,
                'question_text': question.question_text,
                'answer_options': question.answer_options,
                'audio_url': question.word.audio_url if question.question_type == 'audio' else None
            }
            question_data.append(data)
        
        return Response({
            'session_id': session.id,
            'questions': question_data,
            'total_questions': len(questions)
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_answer(request, session_id):
    """Submit answer for a quiz question"""
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    
    serializer = SubmitAnswerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    question_id = serializer.validated_data['question_id']
    user_answer = serializer.validated_data['user_answer']
    response_time = serializer.validated_data.get('response_time')
    
    # Get the question
    question = get_object_or_404(QuizQuestion, id=question_id, session=session)
    
    # Submit answer
    is_correct = question.submit_answer(user_answer, response_time)
    
    # Get next question
    next_question = session.questions.filter(
        user_answer='',
        answered_at__isnull=True
    ).first()
    
    response_data = {
        'is_correct': is_correct,
        'correct_answer': question.correct_answer,
        'explanation': f"{question.word.tamil_word} ({question.word.transliteration}) means {question.word.primary_meaning}.",
        'xp_earned': 15 if is_correct else 5,
    }
    
    if next_question:
        response_data['next_question'] = {
            'id': next_question.id,
            'question_type': next_question.question_type,
            'question_text': next_question.question_text,
            'answer_options': next_question.answer_options,
            'audio_url': next_question.word.audio_url if next_question.question_type == 'audio' else None
        }
    else:
        response_data['quiz_completed'] = True
    
    return Response(response_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_quiz(request, session_id):
    """Complete and submit quiz session"""
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    
    if session.is_completed:
        return Response({'error': 'Quiz already completed'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Complete the session
    session.complete_session()
    
    # Check for new achievements
    achievement_service = AchievementService(request.user)
    new_achievements = achievement_service.check_and_award_achievements()
    
    # Get word progress updates
    word_progress_updates = []
    for question in session.questions.all():
        progress = question.word.user_progress.get(user=request.user)
        word_progress_updates.append({
            'word_id': question.word.id,
            'old_mastery': progress.mastery_level,
            'new_mastery': progress.mastery_level,
            'next_review_date': progress.next_review_date.isoformat()
        })
    
    summary_data = {
        'session_summary': {
            'total_questions': session.total_questions,
            'correct_answers': session.correct_answers,
            'accuracy': session.accuracy_percentage,
            'total_time': session.duration_minutes,
            'xp_earned': session.xp_earned,
            'streak_maintained': True,  # TODO: Implement streak logic
            'new_achievements': new_achievements
        },
        'word_progress_updates': word_progress_updates,
        'new_achievements': new_achievements
    }
    
    return Response(summary_data)


class QuizHistoryView(generics.ListAPIView):
    """Get user's quiz history"""
    serializer_class = QuizSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizSession.objects.filter(
            user=self.request.user,
            completed_at__isnull=False
        ).order_by('-completed_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'sessions': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'sessions': serializer.data,
            'total_count': queryset.count()
        })
