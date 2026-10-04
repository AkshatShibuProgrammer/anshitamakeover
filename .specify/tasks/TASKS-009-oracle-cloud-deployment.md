# TASKS-009: Oracle Cloud Deployment & Cloudflare CDN

**Spec:** SPEC-009 | **Plan:** PLAN-009  
**Status:** Pending Execution (Requires Oracle Cloud Account)  
**Total Tasks:** 8

---

## Task Checklist

### TSK-009.01 — Production Settings Module
- [ ] Create `anshita_project/settings_production.py` extending base `settings.py`.
- [ ] Set: `DEBUG = False`, `ALLOWED_HOSTS = ['anshita.in', 'www.anshita.in', 'localhost']`.
- [ ] Set: `SECURE_SSL_REDIRECT = True`, `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`.
- [ ] Set: `SECURE_HSTS_SECONDS = 31536000`, `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`.
- [ ] Load secrets from environment: `SECRET_KEY = os.environ['DJANGO_SECRET_KEY']`.
- [ ] Add `WHATSAPP_PHONE = os.environ.get('WHATSAPP_PHONE', '')`.
- **Acceptance Check:** `DJANGO_SETTINGS_MODULE=anshita_project.settings_production python manage.py check --deploy` returns 0 issues.

### TSK-009.02 — Nginx Configuration File
- [ ] Create `deployment/nginx.conf` with HTTP→HTTPS redirect block.
- [ ] HTTPS server block: SSL certs (Let's Encrypt path), HSTS, X-Frame-Options, X-Content-Type-Options.
- [ ] Static files: `location /static/` → direct alias with `expires 1y; immutable`.
- [ ] Media files: `location /media/` → direct alias with `expires 30d`.
- [ ] Proxy pass: `location /` → `http://unix:/run/gunicorn.sock`.
- [ ] `client_max_body_size 50M`.
- **Acceptance Check:** `nginx -t` on server returns "test is successful".

### TSK-009.03 — Gunicorn Systemd Service
- [ ] Create `deployment/gunicorn.service` systemd unit file.
- [ ] Config: 4 workers, Unix socket (`/run/gunicorn.sock`), log paths.
- [ ] `EnvironmentFile=/var/www/anshita/.env` for secrets injection.
- [ ] Add `RuntimeDirectory=gunicorn` to fix socket permission issues.
- **Acceptance Check:** `systemctl status gunicorn` shows active (running) after server-side `systemctl enable --now gunicorn`.

### TSK-009.04 — Automated Deployment Script
- [ ] Create `deployment/deploy.sh` bash script with `set -e` (fail-fast).
- [ ] Steps: `git pull` → `pip install` → `migrate` → `collectstatic` → `systemctl restart gunicorn`.
- [ ] Add timestamp echo on completion.
- [ ] `chmod +x deployment/deploy.sh`.
- **Acceptance Check:** `./deployment/deploy.sh` runs end-to-end without errors on staging.

### TSK-009.05 — GitHub Actions CI/CD Pipeline
- [ ] Create `.github/workflows/deploy.yml`.
- [ ] Trigger: `push` to `main` branch.
- [ ] Use `appleboy/ssh-action@master` to SSH into Oracle server and run `deploy.sh`.
- [ ] GitHub Secrets required: `ORACLE_HOST`, `ORACLE_USER`, `ORACLE_SSH_KEY`.
- [ ] Add deployment status badge to `README.md`.
- **Acceptance Check:** Push to `main` triggers automatic deployment within 2 minutes.

### TSK-009.06 — Makefile Targets
- [ ] Add `make deploy` target: SSH into Oracle server and run `deploy.sh`.
- [ ] Add `make check-prod` target: `DJANGO_SETTINGS_MODULE=...settings_production python manage.py check --deploy`.
- [ ] Add `make collectstatic` target: `python manage.py collectstatic --noinput`.
- [ ] Add `make ssl-renew` target: `ssh oracle "certbot renew --quiet"`.
- **Acceptance Check:** `make check-prod` passes with 0 issues.

### TSK-009.07 — Requirements Compatibility Check
- [ ] Audit `requirements.txt` for any x86-only binary packages.
- [ ] Ensure `Pillow>=10.0`, `gunicorn>=21.0`, `whitenoise>=6.5` are specified.
- [ ] Remove `playwright` from production requirements (test-only).
- [ ] Create `requirements-dev.txt` for development-only deps (playwright, coverage, etc.).
- **Acceptance Check:** `pip install -r requirements.txt` succeeds on Ubuntu ARM64 (aarch64).

### TSK-009.08 — Cloudflare Configuration Documentation
- [ ] Create `deployment/CLOUDFLARE_SETUP.md` documenting:
  - DNS record setup (A records → Oracle Elastic IP, proxied).
  - SSL mode: Full (Strict).
  - Page Rule: `/static/*` → Cache Everything, Edge TTL 1 month.
  - Disable Rocket Loader (Page Rule).
  - Always Use HTTPS (toggle in dashboard).
- [ ] Add Cloudflare free tier limits note.
- **Acceptance Check:** Documentation reviewed and verified against Cloudflare dashboard settings.
