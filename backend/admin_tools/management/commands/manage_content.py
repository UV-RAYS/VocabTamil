"""
Django management command for content management
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from vocabulary.models import Word, WordList, WordListItem
from gamification.models import Achievement
from accounts.models import User
import csv
import json


class Command(BaseCommand):
    help = 'Manage VocabTamil content (words, achievements, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            required=True,
            choices=['import_words', 'export_words', 'create_achievement', 'user_stats', 'cleanup'],
            help='Action to perform'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='CSV file path for import/export operations'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Word category for filtering'
        )
        parser.add_argument(
            '--difficulty',
            type=int,
            choices=[1, 2, 3, 4, 5],
            help='Difficulty level for filtering'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'import_words':
            self.import_words(options['file'])
        elif action == 'export_words':
            self.export_words(options['file'], options.get('category'), options.get('difficulty'))
        elif action == 'create_achievement':
            self.create_sample_achievements()
        elif action == 'user_stats':
            self.show_user_stats()
        elif action == 'cleanup':
            self.cleanup_data()

    def import_words(self, file_path):
        """Import words from CSV file"""
        if not file_path:
            self.stdout.write(self.style.ERROR('File path is required for import'))
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                words_created = 0
                
                with transaction.atomic():
                    for row in reader:
                        word, created = Word.objects.get_or_create(
                            tamil_word=row['tamil_word'],
                            defaults={
                                'english_meaning': row['english_meaning'],
                                'pronunciation': row.get('pronunciation', ''),
                                'category': row.get('category', 'general'),
                                'difficulty_level': int(row.get('difficulty_level', 1)),
                                'frequency_rank': int(row.get('frequency_rank', 1000)),
                                'example_sentence_tamil': row.get('example_sentence_tamil', ''),
                                'example_sentence_english': row.get('example_sentence_english', ''),
                                'audio_url': row.get('audio_url', ''),
                            }
                        )
                        
                        if created:
                            words_created += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {words_created} new words')
                )
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Import failed: {str(e)}'))

    def export_words(self, file_path, category=None, difficulty=None):
        """Export words to CSV file"""
        if not file_path:
            self.stdout.write(self.style.ERROR('File path is required for export'))
            return

        try:
            queryset = Word.objects.all()
            
            if category:
                queryset = queryset.filter(category=category)
            if difficulty:
                queryset = queryset.filter(difficulty_level=difficulty)

            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'tamil_word', 'english_meaning', 'pronunciation', 'category',
                    'difficulty_level', 'frequency_rank', 'example_sentence_tamil',
                    'example_sentence_english', 'audio_url'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for word in queryset:
                    writer.writerow({
                        'tamil_word': word.tamil_word,
                        'english_meaning': word.english_meaning,
                        'pronunciation': word.pronunciation,
                        'category': word.category,
                        'difficulty_level': word.difficulty_level,
                        'frequency_rank': word.frequency_rank,
                        'example_sentence_tamil': word.example_sentence_tamil,
                        'example_sentence_english': word.example_sentence_english,
                        'audio_url': word.audio_url,
                    })
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully exported {queryset.count()} words to {file_path}')
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Export failed: {str(e)}'))

    def create_sample_achievements(self):
        """Create sample achievements"""
        achievements_data = [
            {
                'name': 'First Steps',
                'description': 'Complete your first quiz',
                'icon': '🎯',
                'xp_reward': 50,
                'condition_type': 'quiz_completed',
                'condition_value': 1
            },
            {
                'name': 'Word Collector',
                'description': 'Learn 50 words',
                'icon': '📚',
                'xp_reward': 200,
                'condition_type': 'words_learned',
                'condition_value': 50
            },
            {
                'name': 'Quiz Master',
                'description': 'Complete 10 quizzes',
                'icon': '🏆',
                'xp_reward': 300,
                'condition_type': 'quiz_completed',
                'condition_value': 10
            },
            {
                'name': 'Streak Warrior',
                'description': 'Maintain a 7-day learning streak',
                'icon': '🔥',
                'xp_reward': 400,
                'condition_type': 'streak_days',
                'condition_value': 7
            },
            {
                'name': 'Perfect Score',
                'description': 'Get 100% accuracy in a quiz',
                'icon': '⭐',
                'xp_reward': 150,
                'condition_type': 'quiz_accuracy',
                'condition_value': 100
            }
        ]

        created_count = 0
        with transaction.atomic():
            for achievement_data in achievements_data:
                achievement, created = Achievement.objects.get_or_create(
                    name=achievement_data['name'],
                    defaults=achievement_data
                )
                if created:
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} new achievements')
        )

    def show_user_stats(self):
        """Show user statistics"""
        total_users = User.objects.count()
        active_users = User.objects.filter(last_login__isnull=False).count()
        total_words = Word.objects.count()
        total_achievements = Achievement.objects.count()

        self.stdout.write(self.style.SUCCESS('=== VocabTamil Statistics ==='))
        self.stdout.write(f'Total Users: {total_users}')
        self.stdout.write(f'Active Users: {active_users}')
        self.stdout.write(f'Total Words: {total_words}')
        self.stdout.write(f'Total Achievements: {total_achievements}')

        # Category breakdown
        categories = Word.objects.values_list('category', flat=True).distinct()
        self.stdout.write('\n=== Words by Category ===')
        for category in categories:
            count = Word.objects.filter(category=category).count()
            self.stdout.write(f'{category}: {count} words')

        # Difficulty breakdown
        self.stdout.write('\n=== Words by Difficulty ===')
        for level in range(1, 6):
            count = Word.objects.filter(difficulty_level=level).count()
            self.stdout.write(f'Level {level}: {count} words')

    def cleanup_data(self):
        """Clean up old or invalid data"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Clean up old quiz sessions (older than 30 days)
        cutoff_date = timezone.now() - timedelta(days=30)
        
        from quizzes.models import QuizSession
        old_sessions = QuizSession.objects.filter(
            started_at__lt=cutoff_date,
            is_completed=True
        )
        
        deleted_count = old_sessions.count()
        old_sessions.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {deleted_count} old quiz sessions')
        )

        # Remove words without English meanings
        invalid_words = Word.objects.filter(english_meaning__isnull=True)
        invalid_count = invalid_words.count()
        invalid_words.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Removed {invalid_count} invalid words')
        )
