from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('refresh/', views.refresh_token, name='refresh_token'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('stats/', views.UserStatsView.as_view(), name='user_stats'),
    path('achievements/', views.UserAchievementsView.as_view(), name='user_achievements'),
]
