# 🚀 Render Deployment Guide

## Step 1: Select Service Type
- Click **"New Web Service →"** on the Render dashboard

## Step 2: Connect Repository
- Connect your GitHub repository containing this Django project
- Select the repository branch (usually `main` or `master`)

## Step 3: Configure Service

### Basic Settings:
- **Name**: `multi-purpose-business-app` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)

### Build & Deploy Settings:
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn business_app.wsgi:application`

## Step 4: Environment Variables

Add these environment variables in Render dashboard:

### Required Variables:
```
SECRET_KEY=your-very-long-secret-key-here
DEBUG=False
DEBUG_INVENTORY=False
```

### Database (if using Render Postgres):
```
DATABASE_URL=postgresql://user:password@host:port/database
```

### Render Specific:
```
RENDER_EXTERNAL_HOSTNAME=your-app-name.onrender.com
```

### Optional Email Settings:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
SERVER_EMAIL=noreply@yourdomain.com
```

## Step 5: Add Database (Recommended)

1. Go to your Render dashboard
2. Click **"New +"** → **"Postgres"**
3. Configure the database:
   - **Name**: `business-app-db`
   - **Database**: `business_app`
   - **User**: `business_app_user`
4. Copy the **Internal Database URL** from the database settings
5. Add it as `DATABASE_URL` environment variable in your web service

## Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Install dependencies from `requirements.txt`
   - Run the build script (`build.sh`)
   - Start the application with gunicorn
   - Provide you with a public URL

## Step 7: Post-Deployment

### Create Superuser:
1. Go to your Render dashboard
2. Open the **Shell** for your web service
3. Run: `python manage.py createsuperuser`

### Verify Deployment:
1. Visit your app URL (e.g., `https://your-app-name.onrender.com`)
2. Register a new account or login with superuser
3. Test all major features

## Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check that `requirements.txt` exists
   - Verify `build.sh` has execute permissions
   - Check build logs in Render dashboard

2. **Database Connection Issues**:
   - Ensure `DATABASE_URL` is set correctly
   - Verify database is created and accessible
   - Check if migrations ran successfully

3. **Static Files Not Loading**:
   - Verify `STATIC_ROOT` is set correctly
   - Check that `collectstatic` ran during build
   - Ensure WhiteNoise is configured

4. **500 Errors**:
   - Check application logs in Render dashboard
   - Verify all environment variables are set
   - Check if `SECRET_KEY` is properly configured

### Useful Commands (via Render Shell):
```bash
# Check Django status
python manage.py check --deploy

# Run migrations manually
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --no-input

# Check environment variables
python -c "import os; print(os.environ.get('DATABASE_URL', 'Not set'))"
```

## Performance Optimization

### For Production:
1. **Enable Auto-Deploy**: Turn on auto-deploy for your branch
2. **Set up Monitoring**: Use Render's built-in monitoring
3. **Configure Logging**: Check logs regularly for issues
4. **Database Optimization**: Consider read replicas for high traffic

### Scaling:
- **Free Tier**: 750 hours/month, sleeps after 15 minutes of inactivity
- **Paid Plans**: Always-on, better performance, custom domains

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` configured
- [ ] HTTPS enabled (automatic on Render)
- [ ] Database credentials secure
- [ ] Email settings configured (if needed)

## Support

- **Render Documentation**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Render Status**: https://status.render.com

---

**🎉 Your Django application is now deployed and ready for production use!**
