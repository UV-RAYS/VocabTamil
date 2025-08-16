import random
from django.db.models import Q
from vocabulary.models import Word, UserWordProgress
from .models import QuizSession, QuizQuestion


class QuizGeneratorService:
    """Service for generating quiz questions"""
    
    def __init__(self, user):
        self.user = user
    
    def generate_daily_quiz(self, word_ids, question_types=None):
        """Generate a daily practice quiz"""
        if question_types is None:
            question_types = ['mcq', 'fill_blank', 'audio']
        
        words = Word.objects.filter(id__in=word_ids)
        
        # Create quiz session
        session = QuizSession.objects.create(
            user=self.user,
            quiz_type='daily',
            total_questions=len(words)
        )
        
        # Generate questions
        questions = []
        for word in words:
            question_type = random.choice(question_types)
            question = self._generate_question(session, word, question_type)
            questions.append(question)
        
        return session, questions
    
    def _generate_question(self, session, word, question_type):
        """Generate a single question for a word"""
        if question_type == 'mcq':
            return self._generate_mcq(session, word)
        elif question_type == 'fill_blank':
            return self._generate_fill_blank(session, word)
        elif question_type == 'audio':
            return self._generate_audio_question(session, word)
        elif question_type == 'typing':
            return self._generate_typing_question(session, word)
        else:
            return self._generate_mcq(session, word)  # Default fallback
    
    def _generate_mcq(self, session, word):
        """Generate multiple choice question"""
        # Randomly choose direction: Tamil->English or English->Tamil
        tamil_to_english = random.choice([True, False])
        
        if tamil_to_english:
            question_text = f"What does '{word.tamil_word}' mean?"
            correct_answer = word.primary_meaning
            
            # Get wrong options from other words
            wrong_options = list(Word.objects.exclude(
                id=word.id
            ).values_list('meanings__0', flat=True)[:3])
            
            # Flatten and clean wrong options
            wrong_options = [opt for opt in wrong_options if opt and opt != correct_answer][:3]
            
        else:
            question_text = f"How do you say '{word.primary_meaning}' in Tamil?"
            correct_answer = word.tamil_word
            
            # Get wrong options
            wrong_options = list(Word.objects.exclude(
                id=word.id
            ).values_list('tamil_word', flat=True)[:3])
        
        # Ensure we have enough options
        while len(wrong_options) < 3:
            wrong_options.append(f"Option {len(wrong_options) + 1}")
        
        # Create answer options
        all_options = [correct_answer] + wrong_options[:3]
        random.shuffle(all_options)
        
        return QuizQuestion.objects.create(
            session=session,
            word=word,
            question_type='mcq',
            question_text=question_text,
            correct_answer=correct_answer,
            answer_options=all_options
        )
    
    def _generate_fill_blank(self, session, word):
        """Generate fill in the blank question"""
        if word.example_tamil and word.example_english:
            # Use the example sentence
            question_text = f"Complete: {word.example_tamil.replace(word.tamil_word, '____')}"
            correct_answer = word.tamil_word
        else:
            # Create a simple fill-in-the-blank
            question_text = f"Complete: நான் _____ செய்கிறேன் (I am doing _____)"
            correct_answer = word.transliteration
        
        return QuizQuestion.objects.create(
            session=session,
            word=word,
            question_type='fill_blank',
            question_text=question_text,
            correct_answer=correct_answer
        )
    
    def _generate_audio_question(self, session, word):
        """Generate audio recognition question"""
        question_text = f"Listen and type what you hear:"
        correct_answer = word.tamil_word
        
        return QuizQuestion.objects.create(
            session=session,
            word=word,
            question_type='audio',
            question_text=question_text,
            correct_answer=correct_answer
        )
    
    def _generate_typing_question(self, session, word):
        """Generate typing question"""
        question_text = f"Type the Tamil word for: {word.primary_meaning}"
        correct_answer = word.tamil_word
        
        return QuizQuestion.objects.create(
            session=session,
            word=word,
            question_type='typing',
            question_text=question_text,
            correct_answer=correct_answer
        )
