# GitHub Repository Setup and Railway Deployment Guide

## Step 1: Create GitHub Repository

### Option A: Using GitHub Desktop (Recommended)

1. **Open GitHub Desktop**
   - Press `Windows + R`, type `github desktop`, and press Enter
   - Or search for "GitHub Desktop" in the Start menu

2. **Sign in to GitHub** (if not already signed in)
   - Use your GitHub credentials

3. **Create New Repository**
   - Click "File" → "New Repository" or press `Ctrl + N`
   - Fill in the following details:
     - **Name**: `multi-purpose-business-app`
     - **Description**: `A comprehensive Django-based business management system`
     - **Local path**: `C:\Users\CITY GRAPHIC\Desktop\multi_purpose_app updated`
     - **Git ignore**: Select "Python"
     - **License**: Choose "MIT License"
   - Click "Create Repository"

4. **Publish Repository**
   - Click "Publish repository"
   - Make sure "Keep this code private" is unchecked (for Railway deployment)
   - Click "Publish Repository"

### Option B: Using GitHub Website

1. **Go to GitHub.com**
   - Open your browser and go to https://github.com
   - Sign in to your account

2. **Create New Repository**
   - Click the "+" icon in the top right corner
   - Select "New repository"
   - Fill in:
     - **Repository name**: `multi-purpose-business-app`
     - **Description**: `A comprehensive Django-based business management system`
     - **Visibility**: Public
     - **Add a README file**: No (we already have one)
     - **Add .gitignore**: No (we already have one)
     - **Choose a license**: MIT License
   - Click "Create repository"

3. **Connect Local Repository**
   - Copy the repository URL (it will look like: `https://github.com/yourusername/multi-purpose-business-app.git`)
   - In your terminal, run:
     ```bash
     git remote add origin https://github.com/yourusername/multi-purpose-business-app.git
     git branch -M main
     git push -u origin main
     ```

## Step 2: Deploy to Railway

### Option A: Using Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Railway Project**
   ```bash
   railway init
   ```

4. **Deploy the Application**
   ```bash
   railway up
   ```

5. **Set Environment Variables**
   ```bash
   railway variables set SECRET_KEY=your-production-secret-key-here
   railway variables set DEBUG=False
   ```

6. **Run Migrations**
   ```bash
   railway run python manage.py migrate
   ```

7. **Create Superuser**
   ```bash
   railway run python manage.py createsuperuser
   ```

### Option B: Using Railway Dashboard

1. **Go to Railway Dashboard**
   - Visit https://railway.app
   - Sign in with your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `multi-purpose-business-app` repository

3. **Configure Environment Variables**
   - Go to your project settings
   - Add the following variables:
     - `SECRET_KEY`: Generate a secure secret key
     - `DEBUG`: `False`
     - `DATABASE_URL`: Railway will automatically set this

4. **Deploy**
   - Railway will automatically detect it's a Django app
   - It will install dependencies from `requirements.txt`
   - It will use the `Procfile` to start the application

5. **Run Migrations**
   - Go to the "Deployments" tab
   - Click on your latest deployment
   - Open the terminal and run:
     ```bash
     python manage.py migrate
     python manage.py createsuperuser
     ```

## Step 3: Access Your Application

1. **Get Your Railway URL**
   - In the Railway dashboard, you'll see your app URL
   - It will look like: `https://your-app-name.railway.app`

2. **Test Your Application**
   - Visit the URL in your browser
   - You should see your Django application running

## Step 4: Custom Domain (Optional)

1. **Add Custom Domain**
   - In Railway dashboard, go to "Settings"
   - Click "Domains"
   - Add your custom domain

2. **Configure DNS**
   - Point your domain to Railway's servers
   - Follow Railway's DNS configuration instructions

## Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check that all dependencies are in `requirements.txt`
   - Ensure `Procfile` is correctly formatted
   - Check the build logs in Railway dashboard

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is set correctly
   - Check that `dj-database-url` is in requirements.txt

3. **Static Files Not Loading**
   - Ensure `whitenoise` is in requirements.txt
   - Check that `STATIC_ROOT` is set correctly

4. **Environment Variables**
   - Make sure all required environment variables are set in Railway
   - Check that `SECRET_KEY` is set and secure

### Getting Help:

- **Railway Documentation**: https://docs.railway.app
- **Django Documentation**: https://docs.djangoproject.com
- **GitHub Help**: https://help.github.com

## Next Steps

After successful deployment:

1. **Set up monitoring** with Railway's built-in tools
2. **Configure backups** for your database
3. **Set up CI/CD** for automatic deployments
4. **Add SSL certificate** (Railway provides this automatically)
5. **Monitor performance** and optimize as needed

## Security Notes

- Keep your `SECRET_KEY` secure and never commit it to version control
- Use environment variables for all sensitive configuration
- Regularly update dependencies for security patches
- Monitor your application logs for any issues

---

**Need Help?** If you encounter any issues during this process, please refer to the troubleshooting section or contact support.
