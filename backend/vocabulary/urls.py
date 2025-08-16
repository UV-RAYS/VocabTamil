from django.urls import path
from . import views

urlpatterns = [
    path('daily/', views.DailyWordsView.as_view(), name='daily_words'),
    path('review/', views.ReviewWordsView.as_view(), name='review_words'),
    path('weak/', views.WeakWordsView.as_view(), name='weak_words'),
    path('search/', views.WordSearchView.as_view(), name='word_search'),
    path('<int:word_id>/mark-learned/', views.mark_word_learned, name='mark_word_learned'),
    path('lists/', views.WordListView.as_view(), name='word_lists'),
    path('lists/<int:pk>/', views.WordListDetailView.as_view(), name='word_list_detail'),
]
