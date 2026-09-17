# 🌐 Always-Free Minimal Space & Power Hosting Guide

This guide describes how to host **Anshita Makeover** 24/7 on 100% free virtual hosting with minimal RAM (<60MB) and CPU consumption.

---

## Architecture Efficiency
- **Memory Footprint**: Under ~45MB idle RAM.
- **Server Engine**: Gunicorn with threaded workers (`--workers 2 --threads 2 --worker-class gthread`).
- **Static Assets**: Compressed & cached at the application boundary via WhiteNoise.
- **Database**: Zero-overhead embedded SQLite (no separate database server instance required).

---

## Option 1: Render.com (Recommended Free Tier)
Render offers a free tier web service with automatic TLS/SSL, continuous deployment from GitHub, and HTTP/2 support.

### Deployment Steps:
1. **Push code to GitHub**:
   Ensure `anshita_project/` with `Procfile` and `render.yaml` is pushed to your GitHub repository.
2. **Sign up / Log in to [Render.com](https://render.com)**.
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Set:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn anshita_project.wsgi:application --workers 2 --threads 2 --worker-class gthread --timeout 60`
   - **Plan**: `Free (512MB RAM, 0.1 CPU)`
6. Add Environment Variables:
   - `DEBUG`: `False`
   - `DJANGO_ALLOWED_HOSTS`: `.onrender.com`
   - `SECRET_KEY`: `(click generate or provide a secure key)`
7. Click **Create Web Service**. Your site will be live at `https://anshitamakeover.onrender.com` with free automated HTTPS!

---

## Option 2: PythonAnywhere (Always-Free No-Sleep Tier)
PythonAnywhere offers an always-on free account tailored specifically for Python & Django without container spin-down.

### Deployment Steps:
1. Register a free account at [PythonAnywhere.com](https://www.pythonanywhere.com).
2. Open a Bash console and clone your repo:
   ```bash
   git clone <your-repo-url>
   cd anshitamakeover/anshita_project
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic
   ```
3. Go to the **Web** tab:
   - Add a new web app using **Manual configuration (Python 3.10/3.11)**.
   - Set **Virtualenv path**: `/home/yourusername/anshitamakeover/anshita_project/venv`
   - Edit the **WSGI configuration file**:
     ```python
     import os
     import sys
     path = '/home/yourusername/anshitamakeover/anshita_project'
     if path not in sys.path:
         sys.path.append(path)
     os.environ['DJANGO_SETTINGS_MODULE'] = 'anshita_project.settings'
     from django.core.wsgi import get_wsgi_application
     application = get_wsgi_application()
     ```
   - Set **Static Files**:
     - URL: `/static/`
     - Directory: `/home/yourusername/anshitamakeover/anshita_project/staticfiles`
     - URL: `/media/`
     - Directory: `/home/yourusername/anshitamakeover/anshita_project/media`
4. Click **Reload yourusername.pythonanywhere.com** — instant always-free hosting with zero sleep timer!

---

## Option 3: Fly.io (Micro VM < 256MB)
Fly.io provides free allowances for lightweight micro-VMs:
```bash
fly launch
fly deploy
```

---

## Performance Monitoring & Optimization Tips
1. **Gzip / Brotli compression**: Enabled via `whitenoise.storage.CompressedManifestStaticFilesStorage`.
2. **Browser Caching**: Static assets are fingerprinted with max-age headers for 1-year caching.
3. **Low Power Mode**: Web workers sleep when idle, waking instantly upon incoming HTTP requests.
