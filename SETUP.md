# VocabTamil Setup Guide

## Quick Start for Testers

This guide will get VocabTamil running locally in under 10 minutes.

## Prerequisites

- Python 3.9+ 
- Node.js 18+
- PostgreSQL 13+
- Git

## Backend Setup (Django)

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
# Copy the example file
copy .env.example .env

# Edit .env with your database credentials:
# DB_NAME=vocabtamil
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
```

5. **Create PostgreSQL database**
```sql
-- Connect to PostgreSQL and run:
CREATE DATABASE vocabtamil;
CREATE USER vocabtamil_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE vocabtamil TO vocabtamil_user;
```

6. **Run migrations**
```bash
python manage.py makemigrations accounts
python manage.py makemigrations vocabulary
python manage.py makemigrations quizzes
python manage.py makemigrations gamification
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Load sample data**
```bash
python manage.py shell < scripts/load_sample_data.py
```

9. **Start backend server**
```bash
python manage.py runserver
```

Backend will be running at: http://localhost:8000

## Frontend Setup (React/Next.js)

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm run dev
```

Frontend will be running at: http://localhost:3000

## Testing the Application

### 1. **Access the Application**
- Open http://localhost:3000 in your browser
- You should see the VocabTamil landing page

### 2. **Create Test Account**
- Click "Get Started" or "Register"
- Fill in the registration form
- Choose your Tamil level and daily goal
- Click "Create Account"

### 3. **Test Core Features**

**Dashboard:**
- View your progress stats
- See daily word goals and streaks

**Learning Mode:**
- Go to "Learn" section
- View daily words with Tamil text, transliteration, and meanings
- Click audio buttons to hear pronunciation
- Mark words as learned

**Quiz Mode:**
- Start a quiz with your learned words
- Try different question types (MCQ, fill-in-blank, audio)
- Submit answers and see immediate feedback
- Complete quiz to see results and XP earned

**Progress Tracking:**
- View your learning statistics
- Check mastery levels for different words
- See category-wise progress

**Achievements:**
- Check achievements page
- See progress towards unlocking new badges
- View earned achievements and XP rewards

### 4. **Admin Panel (Optional)**
- Go to http://localhost:8000/admin
- Login with superuser credentials
- Add more Tamil words
- Create custom achievements
- View user progress

## Sample Test Data

The application comes pre-loaded with:
- **12 Tamil words** across different categories (emotions, greetings, education, food)
- **8 achievements** with various unlock criteria
- **Multiple quiz question types** for testing

## API Testing

You can also test the API directly:

```bash
# Get daily words (requires authentication)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/words/daily/

# Start a quiz
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"quiz_type": "daily", "word_ids": [1,2,3], "question_types": ["mcq"]}' \
  http://localhost:8000/api/v1/quiz/start/
```

## Troubleshooting

### Common Issues:

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check database credentials in .env file
   - Verify database exists

2. **Module Not Found Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again

3. **Frontend Build Errors**
   - Delete `node_modules` and run `npm install` again
   - Check Node.js version (requires 18+)

4. **CORS Issues**
   - Ensure both frontend (3000) and backend (8000) are running
   - Check CORS settings in Django settings.py

### Getting Help:

- Check the console logs for detailed error messages
- Verify all services are running on correct ports
- Ensure sample data was loaded successfully

## Production Deployment

For production deployment:

1. **Backend**: Deploy to Heroku, Railway, or DigitalOcean
2. **Frontend**: Deploy to Vercel or Netlify
3. **Database**: Use managed PostgreSQL (AWS RDS, Heroku Postgres)
4. **Media**: Configure AWS S3 for audio files

See `/docs/api.md` for complete API documentation.

## Features Ready for Testing

✅ **User Authentication** (Register, Login, JWT tokens)
✅ **Word Learning** (Daily words, spaced repetition, categories)
✅ **Interactive Quizzes** (MCQ, fill-in-blank, audio, typing)
✅ **Progress Tracking** (XP, streaks, mastery levels)
✅ **Gamification** (Achievements, leaderboards, badges)
✅ **Responsive UI** (Mobile-friendly design)
✅ **Audio Support** (Pronunciation playback)
✅ **Admin Panel** (Content management)

The platform is now **operationally ready** for beta testing!
