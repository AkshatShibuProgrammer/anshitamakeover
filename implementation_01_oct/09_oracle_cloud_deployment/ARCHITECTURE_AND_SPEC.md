# Module 09: Oracle Cloud Always-Free Deployment & Cloudflare CDN

**Spec:** [SPEC-009](../../.specify/specs/SPEC-009-oracle-cloud-deployment.md)  
**Plan:** [PLAN-009](../../.specify/plans/PLAN-009-oracle-cloud-deployment.md)  
**Tasks:** [TASKS-009](../../.specify/tasks/TASKS-009-oracle-cloud-deployment.md)  
**Status:** ⏳ Pending (Requires Oracle Cloud Account Setup)

---

## What This Module Delivers

| Feature | Description |
| :--- | :--- |
| **Oracle Cloud ARM Instance** | 4 OCPUs / 24 GB RAM Always-Free Ampere A1 instance — zero hosting cost |
| **Gunicorn + Nginx Stack** | Production-grade WSGI with Unix socket reverse proxy |
| **Let's Encrypt SSL** | Free auto-renewing HTTPS certificate via Certbot |
| **Cloudflare CDN** | Global edge caching, DDoS protection, origin IP masking |
| **GitHub Actions CI/CD** | Auto-deploy on push to `main` via SSH |
| **Production Settings** | Hardened Django config: HTTPS-only, HSTS, secure cookies |

---

## Infrastructure Architecture

```
Internet
    │
    ▼
Cloudflare (CDN + DDoS + SSL Termination)
    │
    ▼  (proxied traffic)
Oracle Cloud Compute Instance (ARM Ubuntu 22.04)
    │
    ├── Nginx (port 443) ──── Let's Encrypt SSL cert
    │       │
    │       ├── /static/ ─── Direct file serve (WhiteNoise pre-collected)
    │       ├── /media/  ─── Direct file serve
    │       └── /        ─── proxy_pass to Gunicorn socket
    │
    └── Gunicorn (Unix socket) ──── Django WSGI App
            │
            └── SQLite (WAL mode) / PostgreSQL (optional)
```

---

## Key Technical Decisions

1. **ARM64 over x86**: Oracle Always-Free gives 4× more compute with Ampere A1 ARM vs 2 AMD micro instances
2. **SQLite with WAL mode** for production (single-server, low-concurrency salon site — PostgreSQL overkill)
3. **Cloudflare Full (Strict) SSL** — end-to-end encryption including Cloudflare ↔ Oracle segment
4. **Rocket Loader disabled** via Cloudflare Page Rule (breaks Three.js WebGL initialization)
5. **No Docker** — systemd services simpler for always-free single-instance deployment

---

## Files to Create

```
deployment/
├── nginx.conf            ← Production Nginx server block
├── gunicorn.service      ← Systemd service unit
├── deploy.sh             ← Automated deployment script
└── CLOUDFLARE_SETUP.md  ← Step-by-step Cloudflare configuration guide

.github/workflows/
└── deploy.yml            ← GitHub Actions CI/CD pipeline

anshita_project/
└── settings_production.py ← Hardened production Django settings
```

---

## Environment Variables Required (`.env` on server)

```
DJANGO_SECRET_KEY=<generated-50-char-secret>
DJANGO_SETTINGS_MODULE=anshita_project.settings_production
ALLOWED_HOSTS=anshita.in,www.anshita.in
GOOGLE_GEMINI_API_KEY=<your-gemini-key>
WHATSAPP_PHONE=919XXXXXXXXX
DATABASE_URL=sqlite:////var/www/anshita/db.sqlite3
```

---

## Acceptance Test Checklist

- [ ] `https://anshita.in` loads over HTTPS with valid Let's Encrypt cert
- [ ] HTTP → HTTPS redirect works
- [ ] Static files served from `/static/` with `Cache-Control: immutable` header
- [ ] Cloudflare shows cache HIT on second request for `/static/` assets
- [ ] GitHub push to `main` triggers deployment within 2 minutes
- [ ] `make check-prod` passes with 0 issues
- [ ] `systemctl status gunicorn` shows active (running) after reboot
