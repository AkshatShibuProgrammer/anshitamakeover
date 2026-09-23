# 🚀 Free Cloud Deployment & Sharing Guide for Anshita Makeover

This guide explains how you can either share the site with Anshita right now from your laptop for free, or host it 24/7 on a free cloud server so Anshita can access and update services at any time.

---

## ⚠️ Why Can't We Use GitHub Pages?
**GitHub Pages only hosts static files** (HTML, CSS, static client-side JS).
Our project is powered by a Python Django backend connected to an SQLite database, handling real-time data persistence, dynamic pricing calculations, and the Gemini AI Concierge. A static host like GitHub Pages cannot execute Python or save data to a database.

Fortunately, there are **100% free hosting options** designed specifically for Python & Django!

---

## Method 1: Instant Sharing from Your Laptop (Zero Setup, 10 Seconds)
If your Django server is running locally on your laptop and you just want Anshita to fill out her services and packages right now on her phone:

1. Double-click **`share_with_anshita.bat`** (or run `python scripts\share_with_anshita.py`).
2. The script spins up a secure public HTTPS link and formats a WhatsApp message.
3. Copy the link or message and send it to Anshita on WhatsApp!
4. Anshita opens the link on her phone, taps through the customized bridal tabs, fills in services/packages, and taps **Save**. All changes are saved directly into your database.

---

## Method 2: Permanent 24/7 Free Cloud Hosting on Render.com

Render offers a generous **free tier** for web services that will run our Django application and SQLite database without costing anything.

### Pre-configured Files Already in the Project:
- `django/render.yaml`: Blueprint configuration for Render.
- `django/Procfile`: Production Gunicorn web server runner.
- `django/requirements.txt`: Includes Gunicorn & WhiteNoise for static files.

### Steps to Deploy to Render:
1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Add Anshita Makeover with Artist Intake portal"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/anshitamakeover.git
   git push -u origin main
   ```
2. Go to [render.com](https://render.com/) and create a free account.
3. Click **New +** -> **Web Service** -> Connect your GitHub repository.
4. Set the following settings:
   - **Root Directory**: `django`
   - **Build Command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn anshita_project.wsgi:application`
   - **Instance Type**: `Free`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `DJANGO_ALLOWED_HOSTS`: `*`
6. Click **Create Web Service**.
7. In ~2 minutes, Render will provide a permanent URL like `https://anshitamakeover.onrender.com`.
8. Send Anshita:
   `https://anshitamakeover.onrender.com/artist-onboarding/?key=anshita2026`

---

## Method 3: Free Hosting on PythonAnywhere.com
[PythonAnywhere.com](https://www.pythonanywhere.com/) provides free beginner accounts with permanent SQLite support and Python web hosting:
1. Register a free account on PythonAnywhere.
2. Open the Bash console and clone your repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/anshitamakeover.git
   ```
3. Set up a virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 anshita-venv
   pip install -r anshitamakeover/django/requirements.txt
   ```
4. In the **Web** tab, configure the WSGI configuration file to point to `anshita_project.wsgi`.
5. Your app will be live at `https://YOUR_USERNAME.pythonanywhere.com/`.

---

## Artist Portal Features for Anshita
When Anshita visits `/artist-onboarding/?key=anshita2026`:
- **Single-Day Looks**: Add or edit Muhurat Bridal, Sangeet Glam, Reception Couture, etc. Quick-select features like Airbrush, HD Eye Artistry, Couture Hair, Mink Lashes, Draping.
- **Multi-Event Packages**: Bundle 2-day or 3-day events (e.g. Sacred Vivah Duo, Grand Vivah Tri-Couture) with bundled pricing.
- **Studio Privileges**: Set complimentary side makeups for family, outstation travel rates, and direct WhatsApp contact.
- **Immediate Sync**: Whenever she taps "Save", both the main website display and the AI chatbot immediately use the updated pricing and package info!
