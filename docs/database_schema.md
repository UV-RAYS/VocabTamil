# VocabTamil Database Schema

## Core Models

### User Model
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    first_name VARCHAR(30),
    last_name VARCHAR(30),
    
    -- Profile & Settings
    tamil_level VARCHAR(20) DEFAULT 'beginner', -- beginner, intermediate, advanced
    daily_word_goal INTEGER DEFAULT 10,
    ui_language VARCHAR(10) DEFAULT 'en', -- 'en' or 'ta'
    
    -- Gamification
    total_xp INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Word Model
```sql
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    tamil_word VARCHAR(100) NOT NULL,
    transliteration VARCHAR(100) NOT NULL,
    
    -- Meanings (JSON array of strings)
    meanings JSONB NOT NULL, -- ["love", "affection", "kindness"]
    
    -- Examples
    example_tamil TEXT,
    example_english TEXT,
    
    -- Audio
    audio_url VARCHAR(500),
    has_native_audio BOOLEAN DEFAULT FALSE,
    
    -- Categorization
    category VARCHAR(50), -- "nature", "food", "emotions", etc.
    difficulty_level INTEGER DEFAULT 1, -- 1-5 scale
    frequency_rank INTEGER, -- how common the word is
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### UserWordProgress Model
```sql
CREATE TABLE user_word_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
    
    -- Learning Progress
    mastery_level INTEGER DEFAULT 0, -- 0=new, 1=learning, 2=familiar, 3=mastered
    times_seen INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    times_incorrect INTEGER DEFAULT 0,
    
    -- Spaced Repetition
    next_review_date DATE,
    review_interval_days INTEGER DEFAULT 1,
    ease_factor DECIMAL(3,2) DEFAULT 2.50, -- SRS algorithm parameter
    
    -- Performance Metrics
    average_response_time DECIMAL(5,2), -- in seconds
    last_response_time DECIMAL(5,2),
    
    -- Timestamps
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, word_id)
);
```

### QuizSession Model
```sql
CREATE TABLE quiz_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session Details
    quiz_type VARCHAR(30) NOT NULL, -- 'daily', 'review', 'speed', 'custom'
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER DEFAULT 0,
    
    -- Performance
    total_time_seconds INTEGER,
    xp_earned INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Session Data (JSON)
    session_data JSONB -- stores question details, user answers, etc.
);
```

### QuizQuestion Model
```sql
CREATE TABLE quiz_questions (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
    
    -- Question Details
    question_type VARCHAR(30) NOT NULL, -- 'mcq', 'fill_blank', 'match', 'audio'
    question_text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    user_answer TEXT,
    
    -- Options for MCQ (JSON array)
    answer_options JSONB,
    
    -- Performance
    is_correct BOOLEAN,
    response_time_seconds DECIMAL(5,2),
    
    -- Timestamps
    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answered_at TIMESTAMP
);
```

### Achievement Model
```sql
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(50), -- emoji or icon class
    
    -- Unlock Criteria
    criteria_type VARCHAR(30) NOT NULL, -- 'words_learned', 'streak', 'xp', 'accuracy'
    criteria_value INTEGER NOT NULL,
    
    -- Rewards
    xp_reward INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### UserAchievement Model
```sql
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER REFERENCES achievements(id) ON DELETE CASCADE,
    
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, achievement_id)
);
```

### WordList Model (for Teachers)
```sql
CREATE TABLE word_lists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- List Properties
    is_public BOOLEAN DEFAULT FALSE,
    category VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### WordListItem Model
```sql
CREATE TABLE word_list_items (
    id SERIAL PRIMARY KEY,
    word_list_id INTEGER REFERENCES word_lists(id) ON DELETE CASCADE,
    word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
    
    order_index INTEGER DEFAULT 0,
    
    UNIQUE(word_list_id, word_id)
);
```

## Indexes for Performance

```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Word searches
CREATE INDEX idx_words_category ON words(category);
CREATE INDEX idx_words_difficulty ON words(difficulty_level);
CREATE INDEX idx_words_tamil_word ON words(tamil_word);

-- User progress queries
CREATE INDEX idx_user_word_progress_user ON user_word_progress(user_id);
CREATE INDEX idx_user_word_progress_review_date ON user_word_progress(next_review_date);
CREATE INDEX idx_user_word_progress_mastery ON user_word_progress(mastery_level);

-- Quiz performance
CREATE INDEX idx_quiz_sessions_user ON quiz_sessions(user_id);
CREATE INDEX idx_quiz_sessions_date ON quiz_sessions(started_at);

-- Leaderboard queries
CREATE INDEX idx_users_xp ON users(total_xp DESC);
CREATE INDEX idx_users_streak ON users(current_streak DESC);
```

## Sample Data Relationships

1. **User Learning Journey**:
   - User takes placement test → creates initial UserWordProgress records
   - Daily learning → updates mastery_level and SRS parameters
   - Quiz sessions → creates QuizSession and QuizQuestion records

2. **Spaced Repetition Flow**:
   - Correct answer → increase review_interval_days, update next_review_date
   - Incorrect answer → reset interval to 1 day, decrease ease_factor

3. **Gamification**:
   - Quiz completion → award XP, check for achievements
   - Daily activity → maintain/break streak
   - Leaderboard → rank users by total_xp or current_streak
