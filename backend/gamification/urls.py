from django.urls import path
from . import views

urlpatterns = [
    path('achievements/', views.AchievementListView.as_view(), name='achievements'),
    path('achievements/progress/', views.AchievementProgressView.as_view(), name='achievement_progress'),
]
