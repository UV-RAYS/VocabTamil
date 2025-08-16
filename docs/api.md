# VocabTamil API Documentation

## Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.vocabtamil.com/api/v1
```

## Authentication
All authenticated endpoints require JWT token in header:
```
Authorization: Bearer <jwt_token>
```

---

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "tamil_level": "beginner",
  "daily_word_goal": 10
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "tamil_level": "beginner",
    "daily_word_goal": 10,
    "total_xp": 0,
    "current_streak": 0
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### POST /auth/login
Login with email/username and password.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "user": { /* user object */ },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### POST /auth/refresh
Refresh JWT access token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### POST /auth/google
Login/register with Google OAuth.

**Request Body:**
```json
{
  "id_token": "google_oauth_id_token"
}
```

---

## User Profile Endpoints

### GET /users/profile
Get current user's profile and stats.

**Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "tamil_level": "beginner",
  "daily_word_goal": 10,
  "ui_language": "en",
  "total_xp": 1250,
  "current_streak": 7,
  "longest_streak": 15,
  "last_activity_date": "2024-01-15",
  "stats": {
    "words_learned": 45,
    "words_mastered": 12,
    "total_quiz_sessions": 23,
    "average_accuracy": 78.5,
    "total_time_minutes": 340
  }
}
```

### PUT /users/profile
Update user profile.

**Request Body:**
```json
{
  "first_name": "John",
  "daily_word_goal": 15,
  "ui_language": "ta"
}
```

### GET /users/achievements
Get user's earned achievements.

**Response (200):**
```json
{
  "achievements": [
    {
      "id": 1,
      "name": "First Steps",
      "description": "Learn your first 10 words",
      "icon": "🎯",
      "earned_at": "2024-01-10T10:30:00Z",
      "xp_reward": 50
    }
  ]
}
```

---

## Word Learning Endpoints

### GET /words/daily
Get today's words for learning based on user's progress and SRS algorithm.

**Query Parameters:**
- `limit` (optional): Number of words to return (default: user's daily_word_goal)

**Response (200):**
```json
{
  "words": [
    {
      "id": 1,
      "tamil_word": "அன்பு",
      "transliteration": "anbu",
      "meanings": ["love", "affection", "kindness"],
      "example_tamil": "அன்பு மிகுந்த மனிதர்",
      "example_english": "A loving person",
      "audio_url": "https://cdn.vocabtamil.com/audio/anbu.mp3",
      "has_native_audio": true,
      "category": "emotions",
      "difficulty_level": 1,
      "user_progress": {
        "mastery_level": 0,
        "times_seen": 0,
        "is_new": true
      }
    }
  ],
  "total_count": 10,
  "new_words": 6,
  "review_words": 4
}
```

### GET /words/review
Get words that need review based on spaced repetition.

**Response (200):**
```json
{
  "words": [
    {
      "id": 5,
      "tamil_word": "நன்றி",
      "transliteration": "nandri",
      "meanings": ["thanks", "gratitude"],
      "user_progress": {
        "mastery_level": 1,
        "times_seen": 3,
        "times_correct": 2,
        "next_review_date": "2024-01-15",
        "is_due": true
      }
    }
  ]
}
```

### POST /words/{word_id}/mark-learned
Mark a word as learned (seen in learning mode).

**Response (200):**
```json
{
  "success": true,
  "user_progress": {
    "mastery_level": 1,
    "times_seen": 1
  }
}
```

### GET /words/search
Search words by Tamil text, transliteration, or meaning.

**Query Parameters:**
- `q`: Search query
- `category` (optional): Filter by category
- `limit` (optional): Number of results (default: 20)

**Response (200):**
```json
{
  "words": [/* word objects */],
  "total_count": 5
}
```

---

## Quiz Endpoints

### POST /quiz/start
Start a new quiz session.

**Request Body:**
```json
{
  "quiz_type": "daily",
  "word_ids": [1, 2, 3, 4, 5],
  "question_types": ["mcq", "fill_blank", "audio"]
}
```

**Response (201):**
```json
{
  "session_id": 123,
  "questions": [
    {
      "id": 1,
      "word_id": 1,
      "question_type": "mcq",
      "question_text": "What does 'அன்பு' mean?",
      "answer_options": ["love", "hate", "fear", "joy"],
      "audio_url": null
    }
  ],
  "total_questions": 5
}
```

### POST /quiz/{session_id}/answer
Submit answer for a quiz question.

**Request Body:**
```json
{
  "question_id": 1,
  "user_answer": "love",
  "response_time": 3.2
}
```

**Response (200):**
```json
{
  "is_correct": true,
  "correct_answer": "love",
  "explanation": "அன்பு (anbu) means love or affection in Tamil.",
  "xp_earned": 15,
  "next_question": {
    "id": 2,
    "question_type": "fill_blank",
    "question_text": "Complete: நான் உன்னை _____ செய்கிறேன்",
    "hint": "I ___ you (emotion)"
  }
}
```

### POST /quiz/{session_id}/complete
Complete and submit quiz session.

**Response (200):**
```json
{
  "session_summary": {
    "total_questions": 5,
    "correct_answers": 4,
    "accuracy": 80.0,
    "total_time": 45.6,
    "xp_earned": 120,
    "streak_maintained": true,
    "new_achievements": []
  },
  "word_progress_updates": [
    {
      "word_id": 1,
      "old_mastery": 0,
      "new_mastery": 1,
      "next_review_date": "2024-01-18"
    }
  ]
}
```

### GET /quiz/history
Get user's quiz history.

**Query Parameters:**
- `limit` (optional): Number of sessions (default: 20)
- `offset` (optional): Pagination offset

**Response (200):**
```json
{
  "sessions": [
    {
      "id": 123,
      "quiz_type": "daily",
      "total_questions": 5,
      "correct_answers": 4,
      "accuracy": 80.0,
      "xp_earned": 120,
      "completed_at": "2024-01-15T14:30:00Z"
    }
  ],
  "total_count": 45
}
```

---

## Progress & Analytics Endpoints

### GET /progress/dashboard
Get comprehensive progress dashboard data.

**Response (200):**
```json
{
  "daily_progress": {
    "words_learned_today": 8,
    "daily_goal": 10,
    "progress_percentage": 80,
    "streak_count": 7,
    "xp_earned_today": 240
  },
  "weekly_stats": {
    "words_learned": 45,
    "quiz_sessions": 12,
    "total_xp": 1250,
    "average_accuracy": 78.5
  },
  "mastery_breakdown": {
    "new": 120,
    "learning": 45,
    "familiar": 23,
    "mastered": 12
  },
  "category_progress": [
    {
      "category": "emotions",
      "words_learned": 15,
      "mastery_rate": 65.2
    }
  ]
}
```

### GET /progress/weak-words
Get words that user struggles with.

**Response (200):**
```json
{
  "weak_words": [
    {
      "word": {
        "id": 10,
        "tamil_word": "கடினமான",
        "transliteration": "kadinamana",
        "meanings": ["difficult", "hard"]
      },
      "progress": {
        "times_seen": 8,
        "times_correct": 2,
        "accuracy": 25.0,
        "last_incorrect": "2024-01-14T10:00:00Z"
      }
    }
  ]
}
```

---

## Leaderboard Endpoints

### GET /leaderboard/daily
Get daily leaderboard.

**Query Parameters:**
- `limit` (optional): Number of users (default: 50)

**Response (200):**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user": {
        "id": 5,
        "username": "tamil_master",
        "first_name": "Priya"
      },
      "xp_today": 450,
      "words_learned_today": 18
    }
  ],
  "current_user_rank": 12,
  "current_user_xp": 240
}
```

### GET /leaderboard/weekly
Get weekly leaderboard.

### GET /leaderboard/monthly
Get monthly leaderboard.

---

## Word Management Endpoints (Admin/Teacher)

### POST /words
Create a new word (admin only).

**Request Body:**
```json
{
  "tamil_word": "புதிய",
  "transliteration": "pudhiya",
  "meanings": ["new", "fresh", "recent"],
  "example_tamil": "புதிய புத்தகம்",
  "example_english": "New book",
  "category": "adjectives",
  "difficulty_level": 2
}
```

### PUT /words/{word_id}
Update word details (admin only).

### DELETE /words/{word_id}
Delete a word (admin only).

### POST /words/{word_id}/audio
Upload audio file for a word.

---

## Word Lists Endpoints (Teachers)

### GET /word-lists
Get user's created word lists.

### POST /word-lists
Create a new word list.

**Request Body:**
```json
{
  "name": "Grade 5 Tamil Vocabulary",
  "description": "Essential words for 5th grade students",
  "word_ids": [1, 2, 3, 4, 5],
  "is_public": false,
  "category": "education"
}
```

### GET /word-lists/{list_id}
Get word list details and words.

### PUT /word-lists/{list_id}
Update word list.

### DELETE /word-lists/{list_id}
Delete word list.

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": {
    "email": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "authentication_required",
  "message": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "permission_denied",
  "message": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "The requested resource was not found."
}
```

### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

---

## Rate Limiting

- Authentication endpoints: 5 requests per minute
- Quiz endpoints: 100 requests per hour
- General endpoints: 1000 requests per hour

## Pagination

List endpoints support pagination:
```
GET /endpoint?limit=20&offset=40
```

Response includes pagination metadata:
```json
{
  "results": [...],
  "count": 150,
  "next": "http://api.example.com/endpoint?limit=20&offset=60",
  "previous": "http://api.example.com/endpoint?limit=20&offset=20"
}
```
