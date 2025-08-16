from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tamil_level', 
                   'total_xp', 'current_streak', 'is_staff')
    list_filter = ('tamil_level', 'ui_language', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Tamil Learning', {
            'fields': ('tamil_level', 'daily_word_goal', 'ui_language')
        }),
        ('Gamification', {
            'fields': ('total_xp', 'current_streak', 'longest_streak', 'last_activity_date')
        }),
    )
    
    readonly_fields = ('total_xp', 'current_streak', 'longest_streak', 'last_activity_date')
