# 🚀 Deployment Guide - Enhanced Timetable Management System

This guide covers multiple deployment options for your Django application.

## 🟦 1. Render (Recommended - Free Tier Available)

### Why Render?
- ✅ **Free tier** with 512MB RAM
- ✅ **Automatic deployments** from GitHub
- ✅ **Built-in PostgreSQL** database
- ✅ **SSL certificates** included
- ✅ **Easy setup** with minimal configuration

### Deploy to Render:

1. **Sign up at [Render.com](https://render.com)**
2. **Connect your GitHub account**
3. **Create a New Web Service**:
   - Repository: `https://github.com/AdityaPandey-DEV/Smart-Time-Table-Management-System`
   - Branch: `main`
   - Build Command: `./build.sh`
   - Start Command: `gunicorn enhanced_timetable_system.wsgi:application`

4. **Add Environment Variables**:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.onrender.com,localhost
   OPENAI_API_KEY=your-openai-key (optional)
   ```

5. **Create PostgreSQL Database**:
   - Go to Dashboard → New → PostgreSQL
   - Connect it to your web service
   - Database URL will be automatically set

6. **Deploy** - Render will automatically build and deploy!

**Your app will be live at**: `https://your-app-name.onrender.com`

---

## 🟣 2. Heroku (Popular Choice)

### Deploy to Heroku:

1. **Install Heroku CLI**
2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   ```

4. **Add PostgreSQL Database**:
   ```bash
   heroku addons:create heroku-postgresql:essential-0
   ```

5. **Set Environment Variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com,localhost
   ```

6. **Deploy**:
   ```bash
   git push heroku main
   ```

7. **Run Migrations**:
   ```bash
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

**Cost**: ~$5-7/month for basic dyno + database

---

## 🔵 3. Railway (Developer-Friendly)

### Deploy to Railway:

1. **Sign up at [Railway.app](https://railway.app)**
2. **Connect GitHub repository**
3. **Deploy from GitHub**:
   - Select your repository
   - Railway will auto-detect Django
   - Add PostgreSQL service

4. **Environment Variables**:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-app.railway.app,localhost
   ```

5. **Custom Start Command**:
   ```
   gunicorn enhanced_timetable_system.wsgi:application
   ```

**Cost**: Pay-as-you-go pricing, free tier available

---

## 🟢 4. PythonAnywhere (Simple Hosting)

### Deploy to PythonAnywhere:

1. **Sign up at [PythonAnywhere.com](https://pythonanywhere.com)**
2. **Upload your code** via Git or file upload
3. **Create Virtual Environment**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 myenv
   pip install -r requirements.txt
   ```

4. **Configure Web App**:
   - Go to Web tab → Add new web app
   - Choose Django
   - Set source code path
   - Configure WSGI file

5. **Database Setup**:
   - Use MySQL database (included in paid plans)
   - Configure in settings.py

**Cost**: $5/month for basic plan

---

## ⚡ 5. Vercel (Frontend-Focused)

### Deploy to Vercel:

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Create `vercel.json`**:
   ```json
   {
     "builds": [
       {
         "src": "enhanced_timetable_system/wsgi.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "enhanced_timetable_system/wsgi.py"
       }
     ]
   }
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

**Note**: Vercel has limitations with Django static files and databases.

---

## 🔧 General Production Setup

### Security Settings:

Add these to your production environment:

```python
# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Static Files:

Ensure these settings are in `settings.py`:
```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## 🎯 Quick Start - Render Deployment

**For the fastest deployment, I recommend Render:**

1. **Fork/Clone** your repository
2. **Sign up** at [Render.com](https://render.com)
3. **Create Web Service** from GitHub
4. **Set Environment Variables**:
   ```
   SECRET_KEY=django-insecure-your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=*.onrender.com,localhost,127.0.0.1
   ```
5. **Create PostgreSQL Database** and link it
6. **Deploy** - Your app will be live in 5-10 minutes!

---

## 📱 Post-Deployment Checklist

After successful deployment:

- ✅ **Test user registration** and login
- ✅ **Verify admin dashboard** functionality
- ✅ **Check student interface** features
- ✅ **Test AI chat** (if API key configured)
- ✅ **Verify responsive design** on mobile
- ✅ **Set up monitoring** and logging
- ✅ **Configure custom domain** (optional)

---

## 🆘 Troubleshooting

### Common Issues:

1. **Static Files Not Loading**:
   ```bash
   python manage.py collectstatic --no-input
   ```

2. **Database Connection Error**:
   - Check DATABASE_URL environment variable
   - Ensure PostgreSQL addon is connected

3. **Secret Key Error**:
   - Generate new secret key
   - Set SECRET_KEY environment variable

4. **ALLOWED_HOSTS Error**:
   - Add your domain to ALLOWED_HOSTS
   - Include both www and non-www versions

### Need Help?
- Check the deployment platform's documentation
- Review application logs for specific errors
- Ensure all environment variables are set correctly

---

**🎉 Your Enhanced Timetable Management System is now ready for the world!**
