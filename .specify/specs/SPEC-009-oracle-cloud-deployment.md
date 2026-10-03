# SPEC-009: Oracle Cloud Always-Free Deployment & Cloudflare CDN

**Status:** Active  
**Milestone:** Production Launch  
**Constitutions:** `.specify/memory/constitution.md`

---

## 1. Overview & Objective

Deploy Anshita Makeover to **Oracle Cloud Always-Free** tier (ARM-based Ampere A1 4 OCPUs / 24 GB RAM) with **Gunicorn + Nginx** serving the Django application behind **Cloudflare's free CDN**, achieving zero hosting cost with production-grade uptime.

---

## 2. User Stories & Acceptance Criteria

### 2.1 Story: Oracle Cloud Instance Provisioning
* **As the studio owner**, I want the website hosted on a reliable, always-on server at zero cost, accessible at `www.anshita.in` or equivalent domain.
* **Acceptance Criteria:**
  - [ ] Oracle Cloud Always-Free ARM compute instance running Ubuntu 22.04.
  - [ ] 4 OCPUs + 24 GB RAM Ampere A1 configuration (maximum always-free allocation).
  - [ ] SSH key-pair provisioned and stored securely.
  - [ ] Firewall rules: ports 22, 80, 443 open; all others closed.
  - [ ] Elastic IP (Reserved Public IP) assigned and stable across reboots.

### 2.2 Story: Django + Gunicorn + Nginx Stack
* **As a developer**, I want the app to run via Gunicorn WSGI with Nginx as the reverse proxy, so we have production-grade process management and static file serving.
* **Acceptance Criteria:**
  - [ ] `gunicorn anshita_project.wsgi:application --workers 4 --bind unix:/run/gunicorn.sock` running as a systemd service.
  - [ ] Nginx upstream to Gunicorn socket, serving `/static/` and `/media/` directly (WhiteNoise disabled in prod Nginx mode).
  - [ ] Nginx config: `server_name anshita.in www.anshita.in`.
  - [ ] `systemctl enable gunicorn nginx` — auto-starts on reboot.

### 2.3 Story: SSL/TLS via Certbot (Let's Encrypt)
* **As a visitor**, I want to access the website over HTTPS with a valid SSL certificate that auto-renews.
* **Acceptance Criteria:**
  - [ ] Certbot installed and certificate issued: `certbot --nginx -d anshita.in -d www.anshita.in`.
  - [ ] Auto-renewal via cron: `0 12 * * * certbot renew --quiet`.
  - [ ] HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`.

### 2.4 Story: Cloudflare DNS & Edge Caching
* **As a studio owner**, I want Cloudflare to act as a CDN layer in front of the Oracle server, accelerating global page delivery and protecting the origin IP.
* **Acceptance Criteria:**
  - [ ] DNS A record for `anshita.in` and `www.anshita.in` pointing to Oracle Elastic IP (proxied through Cloudflare).
  - [ ] Cloudflare SSL mode: **Full (Strict)**.
  - [ ] Cloudflare Page Rule: `/static/*` → Cache Level: Cache Everything, Browser TTL: 1 year, Edge TTL: 1 month.
  - [ ] Cloudflare Always Use HTTPS rule active.
  - [ ] Rocket Loader disabled (conflicts with Three.js/WebGL scripts).

### 2.5 Story: Production Django Settings & Environment
* **As a developer**, I want all secrets externalised to environment variables and `DEBUG=False` enforced in production.
* **Acceptance Criteria:**
  - [ ] `.env` file on server with `DJANGO_SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `GOOGLE_GEMINI_API_KEY`, `WHATSAPP_PHONE`.
  - [ ] `python manage.py check --deploy` returns zero issues.
  - [ ] `python manage.py collectstatic --noinput` run during deployment.
  - [ ] Database: SQLite in development, PostgreSQL (optional) or SQLite with WAL journal mode in production.
  - [ ] `DJANGO_SETTINGS_MODULE=anshita_project.settings.production` environment variable.

### 2.6 Story: CI/CD Deployment Pipeline
* **As a developer**, I want a simple deployment script so any push to `main` branch deploys the latest code to Oracle Cloud automatically.
* **Acceptance Criteria:**
  - [ ] `deploy.sh` script on server: `git pull origin main && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && systemctl restart gunicorn`.
  - [ ] GitHub Actions workflow (`.github/workflows/deploy.yml`) triggers `deploy.sh` via SSH on push to `main`.
  - [ ] Deployment webhook secret stored in GitHub Secrets.

---

## 3. Technical Constraints

- Oracle Always-Free ARM64 instances require Python packages compiled for `aarch64` — ensure `requirements.txt` has no x86-only binaries.
- `Playwright` browser testing must NOT run on the production server (test-only dependency).
- Maximum file upload size: 50 MB (Nginx `client_max_body_size 50M`).
