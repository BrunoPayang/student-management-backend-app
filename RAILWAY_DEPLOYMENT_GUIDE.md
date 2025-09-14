# Railway Deployment Guide for SchoolConnect

## Prerequisites
- Railway account
- Git repository with your code
- PostgreSQL database (Railway provides this)

## Deployment Steps

### 1. Create Railway Project
1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your SchoolConnect repository

### 2. Add PostgreSQL Database
1. In your Railway project dashboard
2. Click "New" → "Database" → "PostgreSQL"
3. Railway will automatically create a database

### 3. Configure Environment Variables
In your Railway project settings, add these environment variables:

```bash
# Database (Railway will auto-populate DATABASE_URL)
DATABASE_URL=postgresql://username:password@host:port/database

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-railway-domain.railway.app

# Optional: Firebase (if using)
FIREBASE_ENABLED=False
FIREBASE_CREDENTIALS_PATH=
FIREBASE_STORAGE_BUCKET=
FIREBASE_PROJECT_ID=

# Optional: Email (if using)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Optional: Redis (for Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 4. Deploy
Railway will automatically:
1. Run `./build.sh` to install dependencies and migrate
2. Start the application with Gunicorn + Uvicorn
3. Serve static files with WhiteNoise

## Files Created for Railway

### `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python -m gunicorn schoolconnect.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/api/health/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### `Procfile`
```
web: python -m gunicorn schoolconnect.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### `build.sh`
```bash
#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Build completed successfully!"
```

## Health Check
Your application includes a health check endpoint at `/api/health/` that Railway will use to verify the deployment.

## Static Files
- WhiteNoise handles static file serving in production
- Files are compressed and cached for better performance
- No need for external CDN or static file hosting

## Database
- Railway provides PostgreSQL database
- Migrations run automatically during deployment
- Database URL is automatically provided via `DATABASE_URL` environment variable

## Monitoring
- Railway provides built-in monitoring
- Check logs in the Railway dashboard
- Health check endpoint: `https://your-app.railway.app/api/health/`

## Troubleshooting

### Common Issues
1. **Build fails**: Check that all dependencies are in `requirements.txt`
2. **Database connection**: Verify `DATABASE_URL` is set correctly
3. **Static files**: Ensure `collectstatic` runs successfully
4. **Health check fails**: Check that the app starts without errors

### Debug Commands
```bash
# Check logs
railway logs

# Connect to database
railway connect

# Run migrations manually
railway run python manage.py migrate
```

## Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up proper database
- [ ] Configure email settings (if needed)
- [ ] Test all API endpoints
- [ ] Verify static files are served correctly
- [ ] Check health check endpoint

## API Endpoints
Once deployed, your API will be available at:
- **API Root**: `https://your-app.railway.app/api/`
- **Documentation**: `https://your-app.railway.app/api/docs/`
- **Health Check**: `https://your-app.railway.app/api/health/`
- **Schema**: `https://your-app.railway.app/api/schema/`