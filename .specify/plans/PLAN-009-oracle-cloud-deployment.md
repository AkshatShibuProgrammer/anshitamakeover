# PLAN-009: Oracle Cloud Deployment & Cloudflare CDN — Technical Blueprint

**Spec:** [SPEC-009](../specs/SPEC-009-oracle-cloud-deployment.md)  
**Status:** Active  
**Estimated Effort:** 4–6 hours

---

## 1. Files to Touch

| File | Change |
| :--- | :--- |
| `anshita_project/settings_production.py` | Production settings (HTTPS, WhiteNoise, allowed hosts) |
| `deployment/nginx.conf` | Nginx server block configuration (new file) |
| `deployment/gunicorn.service` | Systemd Gunicorn service (new file) |
| `deployment/deploy.sh` | Automated deployment script (new file) |
| `.github/workflows/deploy.yml` | GitHub Actions CI/CD pipeline (new file) |
| `requirements.txt` | Ensure aarch64-compatible package list |
| `Makefile` | Add `make deploy` and `make check-prod` targets |

---

## 2. Architecture

### 2.1 Nginx Configuration (`deployment/nginx.conf`)

```nginx
server {
    listen 80;
    server_name anshita.in www.anshita.in;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name anshita.in www.anshita.in;

    ssl_certificate /etc/letsencrypt/live/anshita.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/anshita.in/privkey.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    location /static/ {
        alias /var/www/anshita/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location /media/ {
        alias /var/www/anshita/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 50M;
}
```

### 2.2 Gunicorn Systemd Service (`deployment/gunicorn.service`)

```ini
[Unit]
Description=Anshita Makeover Gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/anshita
EnvironmentFile=/var/www/anshita/.env
ExecStart=/var/www/anshita/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/run/gunicorn.sock \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    anshita_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 2.3 Deployment Script (`deployment/deploy.sh`)

```bash
#!/bin/bash
set -e
cd /var/www/anshita
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --quiet
python manage.py migrate --noinput
python manage.py collectstatic --noinput
systemctl restart gunicorn
echo "✅ Deployment complete — $(date)"
```

### 2.4 GitHub Actions Pipeline (`.github/workflows/deploy.yml`)

```yaml
name: Deploy to Oracle Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: SSH Deploy
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.ORACLE_HOST }}
          username: ${{ secrets.ORACLE_USER }}
          key: ${{ secrets.ORACLE_SSH_KEY }}
          script: /var/www/anshita/deployment/deploy.sh
```

---

## 3. Phase Sequence

| Phase | Task | Duration |
| :--- | :--- | :--- |
| P9.1 | `settings_production.py` — security, WhiteNoise, DB | 30 min |
| P9.2 | `deployment/nginx.conf` — HTTPS, static, proxy | 30 min |
| P9.3 | `deployment/gunicorn.service` — systemd service | 20 min |
| P9.4 | `deployment/deploy.sh` — automated deploy script | 20 min |
| P9.5 | `.github/workflows/deploy.yml` — CI/CD pipeline | 30 min |
| P9.6 | `Makefile` targets: `make deploy`, `make check-prod` | 20 min |
| P9.7 | `requirements.txt` — verify aarch64 compatibility | 30 min |
| P9.8 | Live deployment test + `check --deploy` verification | 60 min |

---

## 4. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| Oracle ARM64 package incompatibility | Pin `Pillow>=10.0` (aarch64 wheel available) |
| Gunicorn socket permission issues | Set `RuntimeDirectory=gunicorn` in systemd unit |
| Cloudflare Rocket Loader breaks Three.js | Disable Rocket Loader via Cloudflare Page Rule |
| Let's Encrypt rate limit | Use staging flag (`--staging`) first, then production |
