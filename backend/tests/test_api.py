"""
Comprehensive API tests for VocabTamil backend
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .test_utils import (
    UserFactory, WordFactory, QuizSessionFactory, AchievementFactory,
    BaseTestCase, APITestMixin, PerformanceTestMixin
)
from vocabulary.models import Word, UserWordProgress
from quizzes.models import QuizSession, QuizQuestion
from gamification.models import Achievement, UserAchievement

User = get_user_model()


class AuthenticationAPITest(APITestCase, APITestMixin):
    """Test authentication endpoints"""
    
    def test_user_registration(self):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'tamil_level': 'beginner',
            'daily_word_goal': 10
        }
        
        response = self.client.post('/api/accounts/register/', data)
        self.assert_api_success(response, 201)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check response contains tokens
        response_data = response.json()
        self.assertIn('access', response_data)
        self.assertIn('refresh', response_data)
        self.assertIn('user', response_data)
    
    def test_user_login(self):
        """Test user login"""
        user = UserFactory()
        user.set_password('testpass123')
        user.save()
        
        data = {
            'username': user.username,
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/accounts/login/', data)
        self.assert_api_success(response)
        
        response_data = response.json()
        self.assertIn('access', response_data)
        self.assertIn('refresh', response_data)
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        
        response = self.client.post('/api/accounts/login/', data)
        self.assert_api_error(response, 401)
    
    def test_profile_update(self):
        """Test profile update"""
        user = self.authenticate_user()
        
        data = {
            'first_name': 'Updated',
            'tamil_level': 'intermediate',
            'daily_word_goal': 15
        }
        
        response = self.client.patch('/api/accounts/profile/', data)
        self.assert_api_success(response)
        
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.tamil_level, 'intermediate')


class VocabularyAPITest(APITestCase, APITestMixin, PerformanceTestMixin):
    """Test vocabulary endpoints"""
    
    def setUp(self):
        self.user = self.authenticate_user()
        self.words = WordFactory.create_batch(20, difficulty_level=1)
    
    def test_daily_words(self):
        """Test daily words endpoint"""
        with self.assert_query_count(3):  # Optimized query count
            response = self.client.get('/api/vocabulary/daily/')
        
        self.assert_api_success(response)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), self.user.daily_word_goal)
    
    def test_word_search(self):
        """Test word search functionality"""
        # Create a specific word to search for
        word = WordFactory(tamil_word='அன்பு', english_meaning='love')
        
        response = self.client.get('/api/vocabulary/search/?q=அன்பு')
        self.assert_api_success(response)
        
        data = response.json()
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]['tamil_word'], 'அன்பு')
    
    def test_mark_word_learned(self):
        """Test marking word as learned"""
        word = self.words[0]
        
        data = {
            'word_id': word.id,
            'is_correct': True,
            'response_time': 2.5
        }
        
        response = self.client.post('/api/vocabulary/mark-learned/', data)
        self.assert_api_success(response)
        
        # Check progress was created
        self.assertTrue(
            UserWordProgress.objects.filter(user=self.user, word=word).exists()
        )
    
    def test_review_words(self):
        """Test review words endpoint"""
        # Create some progress for words
        for word in self.words[:5]:
            UserWordProgress.objects.create(
                user=self.user,
                word=word,
                mastery_level=2,
                times_seen=3
            )
        
        response = self.client.get('/api/vocabulary/review/')
        self.assert_api_success(response)
        
        data = response.json()
        self.assertGreater(len(data), 0)


class QuizAPITest(APITestCase, APITestMixin, PerformanceTestMixin):
    """Test quiz endpoints"""
    
    def setUp(self):
        self.user = self.authenticate_user()
        self.words = WordFactory.create_batch(10, difficulty_level=1)
    
    def test_start_quiz(self):
        """Test starting a quiz"""
        data = {
            'quiz_type': 'mcq',
            'difficulty_level': 1,
            'question_count': 5
        }
        
        with self.assert_response_time_under(1000):  # Under 1 second
            response = self.client.post('/api/quizzes/start/', data)
        
        self.assert_api_success(response, 201)
        
        response_data = response.json()
        self.assertIn('session_id', response_data)
        self.assertIn('questions', response_data)
        self.assertEqual(len(response_data['questions']), 5)
    
    def test_submit_quiz_answer(self):
        """Test submitting quiz answer"""
        # Start a quiz first
        quiz_data = {
            'quiz_type': 'mcq',
            'difficulty_level': 1,
            'question_count': 3
        }
        
        start_response = self.client.post('/api/quizzes/start/', quiz_data)
        session_data = start_response.json()
        session_id = session_data['session_id']
        question = session_data['questions'][0]
        
        # Submit answer
        answer_data = {
            'question_id': question['id'],
            'user_answer': question['correct_answer'],
            'response_time': 2.5
        }
        
        response = self.client.post(
            f'/api/quizzes/{session_id}/submit-answer/',
            answer_data
        )
        
        self.assert_api_success(response)
        
        response_data = response.json()
        self.assertTrue(response_data['is_correct'])
    
    def test_complete_quiz(self):
        """Test completing a quiz"""
        # Create a quiz session with answered questions
        quiz = QuizSessionFactory(user=self.user, total_questions=3)
        
        # Create answered questions
        for i, word in enumerate(self.words[:3]):
            QuizQuestion.objects.create(
                session=quiz,
                word=word,
                question_type='mcq',
                question_text=f"What does '{word.tamil_word}' mean?",
                correct_answer=word.english_meaning,
                user_answer=word.english_meaning if i < 2 else 'wrong',
                is_correct=i < 2,
                response_time=2.0
            )
        
        response = self.client.post(f'/api/quizzes/{quiz.id}/complete/')
        self.assert_api_success(response)
        
        response_data = response.json()
        self.assertIn('score', response_data)
        self.assertIn('xp_earned', response_data)
        
        # Check quiz was marked as completed
        quiz.refresh_from_db()
        self.assertTrue(quiz.is_completed)
    
    def test_quiz_history(self):
        """Test quiz history endpoint"""
        # Create some completed quizzes
        QuizSessionFactory.create_batch(3, user=self.user, is_completed=True)
        
        response = self.client.get('/api/quizzes/history/')
        self.assert_api_success(response)
        self.assert_pagination_response(response)
        
        data = response.json()
        self.assertEqual(len(data['results']), 3)


class ProgressAPITest(APITestCase, APITestMixin):
    """Test progress endpoints"""
    
    def setUp(self):
        self.user = self.authenticate_user()
        # Create some progress data
        self.user.total_xp = 500
        self.user.current_streak = 5
        self.user.save()
        
        # Create word progress
        words = WordFactory.create_batch(10)
        for word in words:
            UserWordProgress.objects.create(
                user=self.user,
                word=word,
                mastery_level=3,
                times_seen=5,
                times_correct=4
            )
    
    def test_dashboard_data(self):
        """Test dashboard data endpoint"""
        response = self.client.get('/api/progress/dashboard/')
        self.assert_api_success(response)
        
        data = response.json()
        self.assertIn('total_xp', data)
        self.assertIn('current_streak', data)
        self.assertIn('words_learned', data)
        self.assertIn('accuracy', data)
        
        self.assertEqual(data['total_xp'], 500)
        self.assertEqual(data['current_streak'], 5)
    
    def test_leaderboard(self):
        """Test leaderboard endpoint"""
        # Create other users with different XP
        UserFactory(total_xp=1000)
        UserFactory(total_xp=300)
        UserFactory(total_xp=800)
        
        response = self.client.get('/api/progress/leaderboard/')
        self.assert_api_success(response)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Check leaderboard is sorted by XP (descending)
        xp_values = [user['total_xp'] for user in data]
        self.assertEqual(xp_values, sorted(xp_values, reverse=True))


class GamificationAPITest(APITestCase, APITestMixin):
    """Test gamification endpoints"""
    
    def setUp(self):
        self.user = self.authenticate_user()
        self.achievements = AchievementFactory.create_batch(5)
        
        # Award some achievements to user
        UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievements[0]
        )
    
    def test_achievements_list(self):
        """Test achievements list endpoint"""
        response = self.client.get('/api/gamification/achievements/')
        self.assert_api_success(response)
        
        data = response.json()
        self.assertEqual(len(data), 5)
        
        # Check first achievement is marked as earned
        earned_achievement = next(a for a in data if a['id'] == self.achievements[0].id)
        self.assertTrue(earned_achievement['is_earned'])
    
    def test_achievement_progress(self):
        """Test achievement progress endpoint"""
        response = self.client.get('/api/gamification/achievement-progress/')
        self.assert_api_success(response)
        
        data = response.json()
        self.assertIsInstance(data, list)
        
        # Should only show unearned achievements
        achievement_ids = [a['achievement']['id'] for a in data]
        self.assertNotIn(self.achievements[0].id, achievement_ids)


class ValidationTest(APITestCase, APITestMixin):
    """Test input validation and security"""
    
    def setUp(self):
        self.user = self.authenticate_user()
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        malicious_query = "'; DROP TABLE vocabulary_word; --"
        
        response = self.client.get(f'/api/vocabulary/search/?q={malicious_query}')
        
        # Should not crash and should return safe results
        self.assertIn(response.status_code, [200, 400])
        
        # Verify table still exists
        self.assertTrue(Word.objects.exists() or Word.objects.count() == 0)
    
    def test_xss_protection(self):
        """Test XSS protection in responses"""
        # Create word with potential XSS content
        word = WordFactory(
            tamil_word='<script>alert("xss")</script>',
            english_meaning='safe meaning'
        )
        
        response = self.client.get(f'/api/vocabulary/search/?q={word.tamil_word}')
        self.assert_api_success(response)
        
        # Response should escape HTML
        response_text = response.content.decode()
        self.assertNotIn('<script>', response_text)
    
    def test_rate_limiting(self):
        """Test rate limiting protection"""
        # Make multiple rapid requests
        responses = []
        for _ in range(20):
            response = self.client.get('/api/vocabulary/daily/')
            responses.append(response.status_code)
        
        # Should eventually get rate limited
        self.assertIn(429, responses)
    
    def test_invalid_data_handling(self):
        """Test handling of invalid data"""
        # Test with invalid quiz data
        invalid_data = {
            'quiz_type': 'invalid_type',
            'difficulty_level': 10,  # Out of range
            'question_count': -5     # Negative
        }
        
        response = self.client.post('/api/quizzes/start/', invalid_data)
        self.assert_api_error(response, 400)
        
        # Test with missing required fields
        response = self.client.post('/api/quizzes/start/', {})
        self.assert_api_error(response, 400)


class PerformanceTest(APITestCase, APITestMixin, PerformanceTestMixin):
    """Test API performance"""
    
    def setUp(self):
        self.user = self.authenticate_user()
        # Create large dataset
        self.words = WordFactory.create_batch(100)
    
    def test_daily_words_performance(self):
        """Test daily words endpoint performance"""
        with self.assert_response_time_under(500):  # Under 500ms
            with self.assert_query_count(3):  # Optimized queries
                response = self.client.get('/api/vocabulary/daily/')
        
        self.assert_api_success(response)
    
    def test_quiz_start_performance(self):
        """Test quiz start performance with large word set"""
        data = {
            'quiz_type': 'mcq',
            'difficulty_level': 1,
            'question_count': 10
        }
        
        with self.assert_response_time_under(1000):  # Under 1 second
            response = self.client.post('/api/quizzes/start/', data)
        
        self.assert_api_success(response, 201)
    
    def test_search_performance(self):
        """Test search performance"""
        with self.assert_response_time_under(300):  # Under 300ms
            response = self.client.get('/api/vocabulary/search/?q=test')
        
        self.assert_api_success(response)


class EdgeCaseTest(APITestCase, APITestMixin):
    """Test edge cases and error scenarios"""
    
    def setUp(self):
        self.user = self.authenticate_user()
    
    def test_empty_word_list(self):
        """Test behavior with empty word list"""
        # Delete all words
        Word.objects.all().delete()
        
        response = self.client.get('/api/vocabulary/daily/')
        
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 404])
        
        if response.status_code == 200:
            data = response.json()
            self.assertEqual(len(data), 0)
    
    def test_incomplete_quiz_session(self):
        """Test handling of incomplete quiz sessions"""
        # Start a quiz but don't complete it
        quiz_data = {
            'quiz_type': 'mcq',
            'difficulty_level': 1,
            'question_count': 5
        }
        
        start_response = self.client.post('/api/quizzes/start/', quiz_data)
        session_id = start_response.json()['session_id']
        
        # Try to complete without answering questions
        response = self.client.post(f'/api/quizzes/{session_id}/complete/')
        
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400])
    
    def test_concurrent_quiz_submissions(self):
        """Test handling of concurrent quiz submissions"""
        # This would require threading in a real test
        # For now, just test that duplicate submissions are handled
        quiz_data = {
            'quiz_type': 'mcq',
            'difficulty_level': 1,
            'question_count': 1
        }
        
        start_response = self.client.post('/api/quizzes/start/', quiz_data)
        session_data = start_response.json()
        session_id = session_data['session_id']
        question = session_data['questions'][0]
        
        answer_data = {
            'question_id': question['id'],
            'user_answer': question['correct_answer']
        }
        
        # Submit same answer twice
        response1 = self.client.post(
            f'/api/quizzes/{session_id}/submit-answer/',
            answer_data
        )
        response2 = self.client.post(
            f'/api/quizzes/{session_id}/submit-answer/',
            answer_data
        )
        
        # First should succeed, second should handle gracefully
        self.assert_api_success(response1)
        self.assertIn(response2.status_code, [200, 400, 409])
    
    def test_network_timeout_simulation(self):
        """Test handling of network timeout scenarios"""
        # This would be handled by the frontend cache system
        # Backend should be resilient to partial requests
        
        # Test with incomplete data
        incomplete_data = {
            'quiz_type': 'mcq'
            # Missing required fields
        }
        
        response = self.client.post('/api/quizzes/start/', incomplete_data)
        self.assert_api_error(response, 400)
        
        # Response should include helpful error message
        error_data = response.json()
        self.assertIn('error', error_data)
        self.assertIn('message', error_data)
