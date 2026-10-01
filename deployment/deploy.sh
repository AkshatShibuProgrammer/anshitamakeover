#!/bin/bash
# ============================================================
# Anshita Makeover — Production Deployment Script
# Oracle Cloud Always-Free ARM64 + Gunicorn + Nginx
# ============================================================
set -e  # Exit immediately on any error

DEPLOY_DIR="/var/www/anshita"
VENV="${DEPLOY_DIR}/venv"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "=========================================="
echo "  ANSHITA MAKEOVER — DEPLOYMENT SCRIPT"
echo "  Started: ${TIMESTAMP}"
echo "=========================================="

# 1. Pull latest code
echo ""
echo "📥 [1/6] Pulling latest code from main..."
cd "${DEPLOY_DIR}"
git pull origin main

# 2. Install dependencies
echo ""
echo "📦 [2/6] Installing Python dependencies..."
source "${VENV}/bin/activate"
pip install -r requirements.txt --quiet

# 3. Run database migrations
echo ""
echo "🗄️  [3/6] Running database migrations..."
python manage.py migrate --noinput

# 4. Collect static files
echo ""
echo "📂 [4/6] Collecting static files..."
DJANGO_SETTINGS_MODULE=anshita_project.settings_production \
    python manage.py collectstatic --noinput

# 5. Run production settings check
echo ""
echo "✅ [5/6] Running production settings check..."
DJANGO_SETTINGS_MODULE=anshita_project.settings_production \
    python manage.py check --deploy

# 6. Restart Gunicorn
echo ""
echo "🔄 [6/6] Restarting Gunicorn service..."
sudo systemctl restart gunicorn

echo ""
echo "=========================================="
echo "  ✅ DEPLOYMENT COMPLETE"
echo "  Finished: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
