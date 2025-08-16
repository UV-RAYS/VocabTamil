from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 
                 'first_name', 'last_name', 'tamil_level', 'daily_word_goal')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    words_learned_count = serializers.ReadOnlyField()
    words_mastered_count = serializers.ReadOnlyField()
    average_accuracy = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                 'tamil_level', 'daily_word_goal', 'ui_language',
                 'total_xp', 'current_streak', 'longest_streak',
                 'last_activity_date', 'words_learned_count',
                 'words_mastered_count', 'average_accuracy',
                 'created_at')
        read_only_fields = ('id', 'username', 'email', 'total_xp',
                           'current_streak', 'longest_streak',
                           'last_activity_date', 'created_at')


class UserStatsSerializer(serializers.Serializer):
    words_learned = serializers.IntegerField()
    words_mastered = serializers.IntegerField()
    total_quiz_sessions = serializers.IntegerField()
    average_accuracy = serializers.FloatField()
    total_time_minutes = serializers.IntegerField()
