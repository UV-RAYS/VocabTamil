#!/usr/bin/env python
"""
Script to load sample Tamil words and achievements for testing
Run with: python manage.py shell < scripts/load_sample_data.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vocabtamil.settings')
django.setup()

from vocabulary.models import Word
from gamification.models import Achievement

# Sample Tamil words
SAMPLE_WORDS = [
    {
        'tamil_word': 'அன்பு',
        'transliteration': 'anbu',
        'meanings': ['love', 'affection', 'kindness'],
        'example_tamil': 'அன்பு மிகுந்த மனிதர்',
        'example_english': 'A loving person',
        'category': 'emotions',
        'difficulty_level': 1,
        'frequency_rank': 1
    },
    {
        'tamil_word': 'நன்றி',
        'transliteration': 'nandri',
        'meanings': ['thanks', 'gratitude'],
        'example_tamil': 'உங்களுக்கு நன்றி',
        'example_english': 'Thank you',
        'category': 'emotions',
        'difficulty_level': 1,
        'frequency_rank': 2
    },
    {
        'tamil_word': 'வணக்கம்',
        'transliteration': 'vanakkam',
        'meanings': ['hello', 'greetings', 'namaste'],
        'example_tamil': 'வணக்கம், எப்படி இருக்கீங்க?',
        'example_english': 'Hello, how are you?',
        'category': 'greetings',
        'difficulty_level': 1,
        'frequency_rank': 3
    },
    {
        'tamil_word': 'புத்தகம்',
        'transliteration': 'puththagam',
        'meanings': ['book'],
        'example_tamil': 'நான் புத்தகம் படிக்கிறேன்',
        'example_english': 'I am reading a book',
        'category': 'education',
        'difficulty_level': 1,
        'frequency_rank': 4
    },
    {
        'tamil_word': 'பள்ளி',
        'transliteration': 'palli',
        'meanings': ['school'],
        'example_tamil': 'நான் பள்ளிக்கு போகிறேன்',
        'example_english': 'I am going to school',
        'category': 'education',
        'difficulty_level': 1,
        'frequency_rank': 5
    },
    {
        'tamil_word': 'வீடு',
        'transliteration': 'veedu',
        'meanings': ['house', 'home'],
        'example_tamil': 'என் வீடு பெரியது',
        'example_english': 'My house is big',
        'category': 'places',
        'difficulty_level': 1,
        'frequency_rank': 6
    },
    {
        'tamil_word': 'தண்ணீர்',
        'transliteration': 'thanneer',
        'meanings': ['water'],
        'example_tamil': 'எனக்கு தண்ணீர் வேண்டும்',
        'example_english': 'I need water',
        'category': 'food',
        'difficulty_level': 1,
        'frequency_rank': 7
    },
    {
        'tamil_word': 'சாப்பாடு',
        'transliteration': 'saappaadu',
        'meanings': ['food', 'meal'],
        'example_tamil': 'சாப்பாடு ருசியாக இருக்கிறது',
        'example_english': 'The food is tasty',
        'category': 'food',
        'difficulty_level': 1,
        'frequency_rank': 8
    },
    {
        'tamil_word': 'நேரம்',
        'transliteration': 'neram',
        'meanings': ['time'],
        'example_tamil': 'இப்போது என்ன நேரம்?',
        'example_english': 'What time is it now?',
        'category': 'time',
        'difficulty_level': 2,
        'frequency_rank': 9
    },
    {
        'tamil_word': 'பணம்',
        'transliteration': 'panam',
        'meanings': ['money'],
        'example_tamil': 'என்னிடம் பணம் இல்லை',
        'example_english': 'I don\'t have money',
        'category': 'general',
        'difficulty_level': 2,
        'frequency_rank': 10
    },
    {
        'tamil_word': 'மகிழ்ச்சி',
        'transliteration': 'magizhchi',
        'meanings': ['happiness', 'joy'],
        'example_tamil': 'அவர் மகிழ்ச்சியாக இருக்கிறார்',
        'example_english': 'He is happy',
        'category': 'emotions',
        'difficulty_level': 2,
        'frequency_rank': 11
    },
    {
        'tamil_word': 'கடினமான',
        'transliteration': 'kadinamana',
        'meanings': ['difficult', 'hard'],
        'example_tamil': 'இது கடினமான கேள்வி',
        'example_english': 'This is a difficult question',
        'category': 'adjectives',
        'difficulty_level': 3,
        'frequency_rank': 12
    }
]

# Sample achievements
SAMPLE_ACHIEVEMENTS = [
    {
        'name': 'First Steps',
        'description': 'Learn your first 5 words',
        'icon': '🎯',
        'criteria_type': 'words_learned',
        'criteria_value': 5,
        'xp_reward': 50,
        'badge_color': 'bronze'
    },
    {
        'name': 'Word Explorer',
        'description': 'Learn 25 words',
        'icon': '🗺️',
        'criteria_type': 'words_learned',
        'criteria_value': 25,
        'xp_reward': 100,
        'badge_color': 'silver'
    },
    {
        'name': 'Vocabulary Master',
        'description': 'Learn 100 words',
        'icon': '👑',
        'criteria_type': 'words_learned',
        'criteria_value': 100,
        'xp_reward': 250,
        'badge_color': 'gold'
    },
    {
        'name': 'Streak Starter',
        'description': 'Maintain a 3-day learning streak',
        'icon': '🔥',
        'criteria_type': 'streak',
        'criteria_value': 3,
        'xp_reward': 75,
        'badge_color': 'orange'
    },
    {
        'name': 'Dedicated Learner',
        'description': 'Maintain a 7-day learning streak',
        'icon': '⚡',
        'criteria_type': 'streak',
        'criteria_value': 7,
        'xp_reward': 150,
        'badge_color': 'blue'
    },
    {
        'name': 'Quiz Champion',
        'description': 'Complete 10 quiz sessions',
        'icon': '🏆',
        'criteria_type': 'quiz_sessions',
        'criteria_value': 10,
        'xp_reward': 100,
        'badge_color': 'purple'
    },
    {
        'name': 'Accuracy Expert',
        'description': 'Achieve 90% accuracy',
        'icon': '🎯',
        'criteria_type': 'accuracy',
        'criteria_value': 90,
        'xp_reward': 200,
        'badge_color': 'green'
    },
    {
        'name': 'Emotion Master',
        'description': 'Master 10 emotion words',
        'icon': '❤️',
        'criteria_type': 'category_mastery',
        'criteria_value': 10,
        'criteria_data': {'category': 'emotions'},
        'xp_reward': 125,
        'badge_color': 'pink'
    }
]

def load_sample_data():
    """Load sample words and achievements"""
    print("Loading sample Tamil words...")
    
    # Load words
    for word_data in SAMPLE_WORDS:
        word, created = Word.objects.get_or_create(
            tamil_word=word_data['tamil_word'],
            defaults=word_data
        )
        if created:
            print(f"Created word: {word.tamil_word} ({word.transliteration})")
        else:
            print(f"Word already exists: {word.tamil_word}")
    
    print(f"\nLoaded {len(SAMPLE_WORDS)} words")
    
    print("\nLoading sample achievements...")
    
    # Load achievements
    for achievement_data in SAMPLE_ACHIEVEMENTS:
        achievement, created = Achievement.objects.get_or_create(
            name=achievement_data['name'],
            defaults=achievement_data
        )
        if created:
            print(f"Created achievement: {achievement.name}")
        else:
            print(f"Achievement already exists: {achievement.name}")
    
    print(f"\nLoaded {len(SAMPLE_ACHIEVEMENTS)} achievements")
    print("\nSample data loading complete!")

if __name__ == '__main__':
    load_sample_data()
