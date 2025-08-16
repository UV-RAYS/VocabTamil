from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.StartQuizView.as_view(), name='start_quiz'),
    path('<int:session_id>/answer/', views.submit_answer, name='submit_answer'),
    path('<int:session_id>/complete/', views.complete_quiz, name='complete_quiz'),
    path('history/', views.QuizHistoryView.as_view(), name='quiz_history'),
]
