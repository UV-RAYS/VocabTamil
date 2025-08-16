"""
Test utilities and fixtures for VocabTamil backend tests
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from vocabulary.models import Word, UserWordProgress
from quizzes.models import QuizSession, QuizQuestion
from gamification.models import Achievement, UserAchievement
import factory
from factory.django import DjangoModelFactory
from faker import Faker

User = get_user_model()
fake = Faker()


class UserFactory(DjangoModelFactory):
    """Factory for creating test users"""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    tamil_level = factory.Iterator(['beginner', 'intermediate', 'advanced'])
    daily_word_goal = factory.Iterator([5, 10, 15, 20])
    total_xp = factory.Faker('random_int', min=0, max=1000)
    current_streak = factory.Faker('random_int', min=0, max=30)


class WordFactory(DjangoModelFactory):
    """Factory for creating test words"""
    class Meta:
        model = Word
    
    tamil_word = factory.Faker('word')
    english_meaning = factory.Faker('word')
    pronunciation = factory.LazyAttribute(lambda obj: obj.tamil_word)
    category = factory.Iterator(['emotions', 'greetings', 'education', 'food', 'family'])
    difficulty_level = factory.Iterator([1, 2, 3, 4, 5])
    frequency_rank = factory.Faker('random_int', min=1, max=10000)
    example_sentence_tamil = factory.Faker('sentence')
    example_sentence_english = factory.Faker('sentence')


class UserWordProgressFactory(DjangoModelFactory):
    """Factory for creating test user word progress"""
    class Meta:
        model = UserWordProgress
    
    user = factory.SubFactory(UserFactory)
    word = factory.SubFactory(WordFactory)
    mastery_level = factory.Iterator([0, 1, 2, 3, 4, 5])
    times_seen = factory.Faker('random_int', min=1, max=20)
    times_correct = factory.Faker('random_int', min=0, max=15)
    ease_factor = factory.Faker('pyfloat', min_value=1.3, max_value=3.0)
    interval_days = factory.Faker('random_int', min=1, max=30)


class QuizSessionFactory(DjangoModelFactory):
    """Factory for creating test quiz sessions"""
    class Meta:
        model = QuizSession
    
    user = factory.SubFactory(UserFactory)
    quiz_type = factory.Iterator(['mcq', 'fill_blank', 'match', 'audio', 'speed'])
    difficulty_level = factory.Iterator([1, 2, 3, 4, 5])
    total_questions = factory.Iterator([5, 10, 15, 20])
    correct_answers = factory.Faker('random_int', min=0, max=20)
    is_completed = True
    xp_earned = factory.Faker('random_int', min=10, max=100)


class AchievementFactory(DjangoModelFactory):
    """Factory for creating test achievements"""
    class Meta:
        model = Achievement
    
    name = factory.Faker('catch_phrase')
    description = factory.Faker('sentence')
    icon = factory.Iterator(['🎯', '📚', '🏆', '🔥', '⭐'])
    xp_reward = factory.Iterator([50, 100, 150, 200, 300])
    condition_type = factory.Iterator(['quiz_completed', 'words_learned', 'streak_days'])
    condition_value = factory.Faker('random_int', min=1, max=100)


class BaseTestCase(TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        """Set up test data"""
        self.user = UserFactory()
        self.words = WordFactory.create_batch(10)
        self.achievement = AchievementFactory()
    
    def create_user_with_progress(self, word_count=5):
        """Create a user with word progress"""
        user = UserFactory()
        words = WordFactory.create_batch(word_count)
        
        for word in words:
            UserWordProgressFactory(user=user, word=word)
        
        return user, words
    
    def create_completed_quiz(self, user=None, question_count=5):
        """Create a completed quiz session"""
        if not user:
            user = self.user
        
        quiz = QuizSessionFactory(
            user=user,
            total_questions=question_count,
            correct_answers=question_count - 1  # Almost perfect score
        )
        
        # Create questions for the quiz
        words = WordFactory.create_batch(question_count)
        for i, word in enumerate(words):
            QuizQuestion.objects.create(
                session=quiz,
                word=word,
                question_type='mcq',
                question_text=f"What does '{word.tamil_word}' mean?",
                correct_answer=word.english_meaning,
                user_answer=word.english_meaning if i < question_count - 1 else 'wrong answer',
                is_correct=i < question_count - 1,
                response_time=fake.pyfloat(min_value=1.0, max_value=10.0)
            )
        
        return quiz
    
    def assert_user_has_achievement(self, user, achievement):
        """Assert that user has a specific achievement"""
        self.assertTrue(
            UserAchievement.objects.filter(user=user, achievement=achievement).exists(),
            f"User {user.username} should have achievement {achievement.name}"
        )
    
    def assert_user_xp_increased(self, user, initial_xp, expected_increase):
        """Assert that user's XP increased by expected amount"""
        user.refresh_from_db()
        actual_increase = user.total_xp - initial_xp
        self.assertEqual(
            actual_increase, expected_increase,
            f"Expected XP increase of {expected_increase}, got {actual_increase}"
        )


class APITestMixin:
    """Mixin for API testing utilities"""
    
    def authenticate_user(self, user=None):
        """Authenticate a user for API tests"""
        if not user:
            user = UserFactory()
        self.client.force_authenticate(user=user)
        return user
    
    def assert_api_success(self, response, expected_status=200):
        """Assert API response is successful"""
        self.assertEqual(response.status_code, expected_status)
        self.assertIn('application/json', response.get('Content-Type', ''))
    
    def assert_api_error(self, response, expected_status=400):
        """Assert API response is an error"""
        self.assertEqual(response.status_code, expected_status)
        self.assertIn('error', response.json())
    
    def assert_pagination_response(self, response):
        """Assert response has pagination structure"""
        data = response.json()
        self.assertIn('count', data)
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)


class PerformanceTestMixin:
    """Mixin for performance testing utilities"""
    
    def assert_query_count(self, expected_count):
        """Context manager to assert query count"""
        from django.test.utils import override_settings
        from django.db import connection
        
        class QueryCountContext:
            def __enter__(self):
                self.initial_queries = len(connection.queries)
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                query_count = len(connection.queries) - self.initial_queries
                if query_count != expected_count:
                    queries = connection.queries[self.initial_queries:]
                    query_list = '\n'.join([f"{i+1}. {q['sql']}" for i, q in enumerate(queries)])
                    raise AssertionError(
                        f"Expected {expected_count} queries, got {query_count}:\n{query_list}"
                    )
        
        return QueryCountContext()
    
    def assert_response_time_under(self, max_time_ms):
        """Context manager to assert response time"""
        import time
        
        class ResponseTimeContext:
            def __enter__(self):
                self.start_time = time.time()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                elapsed_ms = (time.time() - self.start_time) * 1000
                if elapsed_ms > max_time_ms:
                    raise AssertionError(
                        f"Response took {elapsed_ms:.2f}ms, expected under {max_time_ms}ms"
                    )
        
        return ResponseTimeContext()


def create_test_data():
    """Create comprehensive test data for manual testing"""
    # Create test users
    beginner_user = UserFactory(
        username='testbeginner',
        email='beginner@test.com',
        tamil_level='beginner',
        daily_word_goal=5
    )
    
    intermediate_user = UserFactory(
        username='testintermediate', 
        email='intermediate@test.com',
        tamil_level='intermediate',
        daily_word_goal=10
    )
    
    advanced_user = UserFactory(
        username='testadvanced',
        email='advanced@test.com', 
        tamil_level='advanced',
        daily_word_goal=15
    )
    
    # Create test words for different categories and difficulties
    categories = ['emotions', 'greetings', 'education', 'food', 'family']
    
    for category in categories:
        for difficulty in range(1, 6):
            WordFactory.create_batch(
                5,
                category=category,
                difficulty_level=difficulty
            )
    
    # Create achievements
    achievements = [
        AchievementFactory(
            name='First Steps',
            description='Complete your first quiz',
            condition_type='quiz_completed',
            condition_value=1,
            xp_reward=50
        ),
        AchievementFactory(
            name='Word Collector',
            description='Learn 50 words',
            condition_type='words_learned',
            condition_value=50,
            xp_reward=200
        ),
        AchievementFactory(
            name='Streak Master',
            description='Maintain a 7-day streak',
            condition_type='streak_days',
            condition_value=7,
            xp_reward=300
        )
    ]
    
    return {
        'users': [beginner_user, intermediate_user, advanced_user],
        'achievements': achievements,
        'word_count': Word.objects.count()
    }
