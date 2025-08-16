# 🚀 VocabTamil Deployment Guide for Beta Testers

## 📋 Quick Start for Testers

VocabTamil is now production-ready! Here's your complete guide to deploy and test the Tamil vocabulary learning platform.

### 🎯 Deployment Options

**Option 1: Cloud Deployment (Recommended)**
- Deploy to Heroku, Railway, or DigitalOcean
- Automatic SSL, scaling, and monitoring
- Best for beta testing with real users

**Option 2: Local Docker Deployment**
- Run locally with Docker Compose
- Perfect for development and testing
- Full production simulation

**Option 3: Manual Server Deployment**
- Deploy to your own VPS/server
- Complete control over infrastructure
- Requires more setup but fully customizable

---

## 🌟 Option 1: Cloud Deployment (Heroku/Railway)

### Step 1: Prepare Your Repository
```bash
# Clone the repository
git clone <your-repo-url>
cd VocabTamil

# Ensure all secrets are secure
cp deployment/.env.example .env
# Edit .env with your production values (see below)
```

### Step 2: Set Up External Services

**Database (PostgreSQL):**
- Heroku: Add Heroku Postgres add-on
- Railway: Enable PostgreSQL service
- Or use external provider like Supabase/Neon

**Redis Cache:**
- Heroku: Add Heroku Redis add-on
- Railway: Enable Redis service
- Or use Redis Cloud

**File Storage (AWS S3):**
```bash
# Create S3 bucket for media files
aws s3 mb s3://vocabtamil-media-prod
aws s3api put-bucket-cors --bucket vocabtamil-media-prod --cors-configuration file://deployment/s3-cors.json
```

### Step 3: Configure Environment Variables

**Required Production Variables:**
```bash
# Django Core
SECRET_KEY=your-unique-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (provided by hosting service)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Redis (provided by hosting service)
REDIS_URL=redis://user:pass@host:port

# AWS S3 Storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=vocabtamil-media-prod
AWS_S3_REGION_NAME=us-east-1

# Google OAuth (for social login)
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret

# Email (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-app-password

# Frontend URL
NEXT_PUBLIC_API_URL=https://your-domain.com/api
```

### Step 4: Deploy Backend
```bash
# For Heroku
heroku create vocabtamil-backend
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
heroku config:set SECRET_KEY=your-secret-key
# ... set all other environment variables
git subtree push --prefix=backend heroku main

# For Railway
railway login
railway new vocabtamil-backend
railway add postgresql redis
railway up --service backend
```

### Step 5: Deploy Frontend
```bash
# For Vercel (recommended for Next.js)
npm install -g vercel
cd frontend
vercel --prod
# Set environment variables in Vercel dashboard

# For Netlify
cd frontend
npm run build
# Deploy dist folder to Netlify
```

---

## 🐳 Option 2: Local Docker Deployment

### Step 1: Prerequisites
```bash
# Install Docker and Docker Compose
# Windows: Docker Desktop
# Mac: Docker Desktop
# Linux: docker.io docker-compose
```

### Step 2: Configuration
```bash
cd deployment
cp .env.example .env

# Edit .env with local values:
SECRET_KEY=local-development-secret-key
DB_PASSWORD=local-db-password
ALLOWED_HOSTS=localhost,127.0.0.1
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# For local testing, you can use dummy AWS credentials
AWS_ACCESS_KEY_ID=local-test-key
AWS_SECRET_ACCESS_KEY=local-test-secret
```

### Step 3: Deploy
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Step 4: Access Your Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/

---

## 🖥️ Option 3: Manual Server Deployment

### Step 1: Server Setup (Ubuntu 20.04+)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm postgresql postgresql-contrib redis-server nginx certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash vocabtamil
sudo usermod -aG sudo vocabtamil
```

### Step 2: Database Setup
```bash
# Configure PostgreSQL
sudo -u postgres createuser --createdb vocabtamil
sudo -u postgres createdb vocabtamil_prod
sudo -u postgres psql -c "ALTER USER vocabtamil PASSWORD 'secure-password';"
```

### Step 3: Application Deployment
```bash
# Clone and setup backend
sudo -u vocabtamil git clone <repo-url> /home/vocabtamil/VocabTamil
cd /home/vocabtamil/VocabTamil/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values

# Run migrations and collect static files
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Setup frontend
cd ../frontend
npm install
npm run build

# Configure systemd services (see deployment/systemd/ folder)
sudo cp deployment/systemd/* /etc/systemd/system/
sudo systemctl enable vocabtamil-backend vocabtamil-frontend vocabtamil-celery
sudo systemctl start vocabtamil-backend vocabtamil-frontend vocabtamil-celery
```

### Step 4: Nginx Configuration
```bash
# Copy nginx config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/vocabtamil
sudo ln -s /etc/nginx/sites-available/vocabtamil /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Setup SSL with Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🧪 Testing Your Deployment

### Step 1: Health Checks
```bash
# Check backend health
curl https://yourdomain.com/api/health/

# Check frontend
curl https://yourdomain.com/

# Check database connection
curl https://yourdomain.com/api/accounts/register/ -X POST -H "Content-Type: application/json" -d '{"username":"test","email":"test@example.com","password":"testpass123"}'
```

### Step 2: Feature Testing
1. **User Registration**: Create a new account
2. **Word Learning**: Access daily words
3. **Quiz System**: Take a vocabulary quiz
4. **Audio Playback**: Test pronunciation features
5. **Progress Tracking**: Check XP and streak tracking
6. **Offline Mode**: Test offline functionality
7. **Tamil/English Toggle**: Switch languages

### Step 3: Performance Testing
```bash
# Install testing tools
pip install locust

# Run performance tests
cd backend
locust -f tests/performance_tests.py --host=https://yourdomain.com
```

---

## 🔧 Configuration for Beta Testing

### Enable Analytics and Monitoring
```bash
# Add to your .env
SENTRY_DSN=your-sentry-dsn-for-error-tracking
ANALYTICS_ENABLED=True

# Google Analytics (optional)
NEXT_PUBLIC_GA_ID=your-google-analytics-id
```

### Set Up User Feedback
```bash
# Enable feedback collection
FEEDBACK_ENABLED=True
FEEDBACK_EMAIL=feedback@yourdomain.com
```

### Configure Content Management
```bash
# Create admin user
python manage.py createsuperuser

# Load sample Tamil words
python manage.py loaddata scripts/load_sample_data.py

# Import custom word lists
python manage.py manage_content --action=import_words --file=your_words.csv
```

---

## 📊 Monitoring and Maintenance

### Daily Monitoring
- Check application health: `curl https://yourdomain.com/api/health/`
- Monitor error logs: `docker-compose logs -f backend`
- Check database performance: Access admin panel → Database stats
- Review user analytics: Check analytics dashboard

### Weekly Maintenance
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Database backup: `python manage.py dbbackup`
- Clear old sessions: `python manage.py clearsessions`
- Review performance metrics

### User Support
- Monitor user feedback through admin panel
- Check error reports in Sentry (if configured)
- Review quiz completion rates and user progress
- Update word content based on user needs

---

## 🆘 Troubleshooting

### Common Issues

**Database Connection Error:**
```bash
# Check database status
sudo systemctl status postgresql
# Check connection string in .env
```

**Static Files Not Loading:**
```bash
# Recollect static files
python manage.py collectstatic --noinput
# Check nginx configuration
```

**Audio Files Not Playing:**
```bash
# Check S3 bucket permissions
# Verify CORS configuration
# Test TTS fallback
```

**Slow Performance:**
```bash
# Check database queries
python manage.py shell -c "from django.db import connection; print(len(connection.queries))"
# Monitor Redis cache hit rate
# Check server resources
```

### Getting Help
- Check logs: `docker-compose logs -f`
- Review error tracking in Sentry
- Test with `.env.testing` for debugging
- Contact support with error details

---

## 🎉 You're Ready!

Your VocabTamil deployment is now ready for beta testing! The platform includes:

✅ **Secure authentication** with JWT and OAuth
✅ **Tamil vocabulary learning** with spaced repetition
✅ **Interactive quizzes** with multiple question types
✅ **Audio pronunciation** with TTS fallback
✅ **Progress tracking** and gamification
✅ **Offline support** for uninterrupted learning
✅ **Accessibility features** for all users
✅ **Admin tools** for content management

**Next Steps:**
1. Share the URL with your beta testers
2. Monitor user feedback and analytics
3. Iterate based on user needs
4. Scale infrastructure as user base grows

Happy testing! 🚀📚
