from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
]
