# VocabTamil - Tamil Vocabulary Learning Platform

A gamified Tamil vocabulary learning platform inspired by Vocabulary.com, featuring adaptive learning, spaced repetition, and interactive quizzes.

## Features

### Core Learning
- Daily word goals with adaptive difficulty
- Interactive word cards with audio pronunciation
- Multiple quiz modes (MCQ, fill-in-blank, match-pairs, audio, speed rounds)
- Spaced repetition algorithm for optimal retention

### Gamification
- XP points and daily streaks
- Leaderboards (daily, weekly, monthly)
- Achievements and virtual rewards
- Progress tracking and analytics

### User Experience
- Responsive web design (mobile-friendly)
- Tamil/English UI toggle
- Accessibility features
- Offline mode support

## Tech Stack

### Frontend
- React with Next.js (SSR)
- TailwindCSS for styling
- Responsive design

### Backend
- Django REST Framework
- PostgreSQL database
- JWT authentication
- AWS S3 for audio storage

### Deployment
- Frontend: Vercel
- Backend: Render/Heroku
- CDN: CloudFront for audio delivery

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL 13+

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd VocabTamil
```

2. Setup Backend
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
VocabTamil/
├── backend/           # Django REST API
├── frontend/          # Next.js React app
├── docs/             # Documentation
├── scripts/          # Utility scripts
└── README.md
```

## API Documentation

See `/docs/api.md` for detailed API endpoints and usage.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
