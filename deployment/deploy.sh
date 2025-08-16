#!/bin/bash

# VocabTamil Production Deployment Script
set -e

echo "🚀 Starting VocabTamil deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found. Please create one with required environment variables."
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=(
    "SECRET_KEY"
    "DB_PASSWORD"
    "ALLOWED_HOSTS"
    "AWS_ACCESS_KEY_ID"
    "AWS_SECRET_ACCESS_KEY"
    "AWS_STORAGE_BUCKET_NAME"
    "NEXT_PUBLIC_API_URL"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required environment variable $var is not set."
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Create necessary directories
mkdir -p ssl
mkdir -p backups

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker-compose pull

# Build custom images
echo "🔨 Building custom images..."
docker-compose build --no-cache

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Start database and redis first
echo "🗄️ Starting database and cache services..."
docker-compose up -d db redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
timeout=60
while ! docker-compose exec -T db pg_isready -U vocabtamil_user -d vocabtamil; do
    sleep 2
    timeout=$((timeout - 2))
    if [ $timeout -le 0 ]; then
        echo "❌ Database failed to start within 60 seconds"
        exit 1
    fi
done

echo "✅ Database is ready"

# Run database migrations
echo "🔄 Running database migrations..."
docker-compose run --rm backend python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose run --rm backend python manage.py collectstatic --noinput

# Load sample data (optional)
if [ "$LOAD_SAMPLE_DATA" = "true" ]; then
    echo "📊 Loading sample data..."
    docker-compose run --rm backend python manage.py loaddata scripts/load_sample_data.py
fi

# Create superuser (if specified)
if [ ! -z "$DJANGO_SUPERUSER_USERNAME" ] && [ ! -z "$DJANGO_SUPERUSER_EMAIL" ] && [ ! -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Creating superuser..."
    docker-compose run --rm backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
fi

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

# Wait for services to be healthy
echo "🏥 Checking service health..."
services=("backend" "frontend")

for service in "${services[@]}"; do
    echo "Checking $service health..."
    timeout=120
    while ! docker-compose exec -T $service curl -f http://localhost:$(docker-compose port $service | cut -d: -f2)/health 2>/dev/null; do
        sleep 5
        timeout=$((timeout - 5))
        if [ $timeout -le 0 ]; then
            echo "❌ $service failed to become healthy within 2 minutes"
            docker-compose logs $service
            exit 1
        fi
    done
    echo "✅ $service is healthy"
done

# Run tests (optional)
if [ "$RUN_TESTS" = "true" ]; then
    echo "🧪 Running tests..."
    docker-compose run --rm backend python manage.py test
fi

# Create backup
echo "💾 Creating initial backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U vocabtamil_user vocabtamil > "backups/backup_${timestamp}.sql"

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000/api/"
echo "- Admin Panel: http://localhost:8000/admin/"
echo "- Database: PostgreSQL on port 5432"
echo "- Cache: Redis on port 6379"
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "📝 Next Steps:"
echo "1. Configure SSL certificates in deployment/ssl/"
echo "2. Update DNS records to point to your server"
echo "3. Set up monitoring and alerting"
echo "4. Configure automated backups"
echo "5. Review logs: docker-compose logs -f"

# Show resource usage
echo ""
echo "💻 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
