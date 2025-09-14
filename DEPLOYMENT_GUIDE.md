# SchoolConnect Deployment Guide

This guide covers deployment options for both Railway and Render platforms.

## 🚀 Railway Deployment

### Files for Railway:
- `railway.json` - Railway configuration
- `Procfile` - Alternative process file
- `build.sh` - Build script

### Quick Deploy to Railway:
1. Push code to GitHub
2. Connect repository to Railway
3. Add PostgreSQL database
4. Set environment variables
5. Deploy automatically

## 🌐 Render Deployment

### Files for Render:
- `render.yaml` - Render configuration
- `build.sh` - Build script (shared)

### Quick Deploy to Render:
1. Push code to GitHub
2. Connect repository to Render
3. Render will auto-detect `render.yaml`
4. Add PostgreSQL database
5. Deploy automatically

## 📋 Environment Variables

Both platforms need these environment variables:

### Required:
```bash
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

### Optional:
```bash
FIREBASE_ENABLED=False
FIREBASE_CREDENTIALS_PATH=
FIREBASE_STORAGE_BUCKET=
FIREBASE_PROJECT_ID=
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 🔧 Build Process

Both platforms use the same `build.sh` script:

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

## 🏥 Health Check

Both platforms use the health check endpoint:
- **URL**: `/api/health/`
- **Response**: `{"status": "healthy", "message": "SchoolConnect API is running"}`

## 📊 Platform Comparison

| Feature | Railway | Render |
|---------|---------|--------|
| **Free Tier** | ✅ | ✅ |
| **PostgreSQL** | ✅ | ✅ |
| **Auto Deploy** | ✅ | ✅ |
| **Custom Domain** | ✅ | ✅ |
| **Environment Variables** | ✅ | ✅ |
| **Logs** | ✅ | ✅ |
| **Health Checks** | ✅ | ✅ |
| **Static Files** | ✅ (WhiteNoise) | ✅ (WhiteNoise) |

## 🚀 Quick Start

### Option 1: Railway
1. Go to [Railway.app](https://railway.app)
2. Connect GitHub repository
3. Add PostgreSQL database
4. Deploy!

### Option 2: Render
1. Go to [Render.com](https://render.com)
2. Connect GitHub repository
3. Render auto-detects `render.yaml`
4. Add PostgreSQL database
5. Deploy!

## 🔍 Troubleshooting

### Common Issues:
1. **Build fails**: Check `requirements.txt` has all dependencies
2. **Database connection**: Verify `DATABASE_URL` is set
3. **Static files**: Ensure `collectstatic` runs successfully
4. **Health check fails**: Check application starts without errors
5. **Migration errors**: Fixed CharField default value issues in schools migration

### Migration Fixes Applied:
1. **CharField Default Values**: Fixed migration using `django.utils.timezone.now` as default for CharField fields
   - `city`: 'Niamey'
   - `state`: 'Niamey' 
   - `contact_email`: 'admin@schoolconnect.ne'
   - `contact_phone`: '+22712345678'

2. **UUID Field Conversion**: Resolved `cannot cast type bigint to uuid` error
   - Changed School model to use `BigAutoField` instead of `UUIDField`
   - This provides better compatibility with existing data and migrations
   - Maintains all functionality while avoiding PostgreSQL casting issues

### Debug Commands:
```bash
# Check logs
railway logs  # Railway
render logs   # Render

# Run migrations manually
railway run python manage.py migrate  # Railway
render run python manage.py migrate   # Render
```

## 📱 API Endpoints

Once deployed, your API will be available at:

- **API Root**: `https://your-app.com/api/`
- **Documentation**: `https://your-app.com/api/docs/`
- **Health Check**: `https://your-app.com/api/health/`
- **Schema**: `https://your-app.com/api/schema/`

## ✅ Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Test all API endpoints
- [ ] Verify static files are served
- [ ] Check health check endpoint
- [ ] Configure email settings (if needed)
- [ ] Set up monitoring

## 🎯 Recommended Platform

**For this project, I recommend Railway** because:
- Better Python/Django support
- More reliable free tier
- Better performance
- Easier configuration

But both platforms will work perfectly with the provided configuration files!
