# Railway Deployment Guide for Multi-Purpose Business Application

## 🚀 Deploy Your Django Business App to Railway

This guide will help you deploy your Django business application to Railway so it can be accessed worldwide.

## Prerequisites

1. **GitHub Account** - Your code is already on GitHub at https://github.com/stevebusinessapp/business
2. **Railway Account** - Sign up at https://railway.app
3. **Git** - For version control

## Step 1: Prepare Your Repository

Your repository is already well-configured for Railway deployment with:
- ✅ `Procfile` - Web server configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version specification
- ✅ Database configuration for PostgreSQL
- ✅ Static files configuration

## Step 2: Deploy to Railway

### Option A: Deploy via Railway Dashboard (Recommended)

1. **Go to Railway Dashboard**
   - Visit https://railway.app
   - Sign in with your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository: `stevebusinessapp/business`

3. **Configure Environment Variables**
   After deployment, go to your project settings and add these environment variables:

   ```bash
   SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
   DEBUG=False
   DEBUG_INVENTORY=False
   DATABASE_URL=postgresql://... (Railway will set this automatically)
   ```

4. **Add PostgreSQL Database**
   - In your Railway project, click "New"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically set the `DATABASE_URL` environment variable

5. **Run Migrations**
   - Go to your project's "Deployments" tab
   - Click on the latest deployment
   - Go to "Variables" tab
   - Add a new variable:
     - Name: `RAILWAY_COMMAND`
     - Value: `python manage.py migrate`

6. **Create Superuser**
   - Add another variable:
     - Name: `RAILWAY_COMMAND`
     - Value: `python manage.py createsuperuser --noinput --username admin --email admin@example.com`

### Option B: Deploy via Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Set Environment Variables**
   ```bash
   railway variables set SECRET_KEY=your-super-secret-key-here
   railway variables set DEBUG=False
   railway variables set DEBUG_INVENTORY=False
   ```

6. **Add Database**
   ```bash
   railway add
   # Select PostgreSQL
   ```

7. **Run Migrations**
   ```bash
   railway run python manage.py migrate
   ```

8. **Create Superuser**
   ```bash
   railway run python manage.py createsuperuser
   ```

## Step 3: Configure Custom Domain (Optional)

1. **Get Your Railway URL**
   - Your app will be available at: `https://your-app-name.railway.app`

2. **Add Custom Domain**
   - In Railway dashboard, go to your project
   - Click "Settings" → "Domains"
   - Add your custom domain

## Step 4: Post-Deployment Setup

### 1. Verify Deployment
- Visit your Railway URL
- Check if the application loads correctly
- Test user registration and login

### 2. Set Up Email (Optional)
If you want email functionality, add these environment variables:
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. Configure Static Files
Your app is already configured with WhiteNoise for static file serving.

## Step 5: Monitor and Maintain

### 1. View Logs
- In Railway dashboard, go to "Deployments"
- Click on any deployment to view logs

### 2. Scale Your App
- Railway automatically scales based on traffic
- You can manually adjust in the dashboard

### 3. Database Backups
- Railway provides automatic PostgreSQL backups
- Access them in the database service settings

## Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version in `runtime.txt`

2. **Database Connection Issues**
   - Ensure `DATABASE_URL` is set correctly
   - Check that migrations have been run

3. **Static Files Not Loading**
   - Verify WhiteNoise is in `MIDDLEWARE`
   - Check `STATIC_ROOT` configuration

4. **500 Server Error**
   - Check Railway logs for detailed error messages
   - Verify all environment variables are set

### Getting Help:
- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Your GitHub Issues: https://github.com/stevebusinessapp/business/issues

## Security Best Practices

1. **Environment Variables**
   - Never commit sensitive data to Git
   - Use Railway's environment variable system

2. **Secret Key**
   - Generate a strong, random secret key
   - Keep it secure and don't share it

3. **Database Security**
   - Railway handles database security automatically
   - Use strong passwords for admin accounts

## Cost Considerations

- Railway offers a free tier with limitations
- Paid plans start at $5/month
- Database storage and bandwidth are included

## Next Steps

After successful deployment:

1. **Test All Features**
   - User registration and login
   - Invoice creation and management
   - Inventory management
   - All other business features

2. **Set Up Monitoring**
   - Configure error tracking (e.g., Sentry)
   - Set up uptime monitoring

3. **Backup Strategy**
   - Regular database backups
   - Code repository backups

4. **Documentation**
   - Update your README with the live URL
   - Document any deployment-specific configurations

---

## 🎉 Congratulations!

Your Django business application is now deployed and accessible worldwide! 

**Your app URL will be:** `https://your-app-name.railway.app`

Share this URL with your users and start managing your business operations online!
