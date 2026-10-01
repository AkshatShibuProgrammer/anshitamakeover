# Cloudflare Setup Guide — Anshita Makeover

**Objective:** Configure Cloudflare as CDN + DDoS protection in front of Oracle Cloud server.

---

## Step 1: Add Domain to Cloudflare

1. Log in to [dash.cloudflare.com](https://dash.cloudflare.com)
2. Click **Add a Site** → enter your domain (e.g., `anshita.in`)
3. Select **Free** plan
4. Cloudflare will scan existing DNS records — review them

---

## Step 2: DNS Record Configuration

Set these A records (proxied ☁️, not DNS-only):

| Type | Name | Value | Proxy Status |
| :--- | :--- | :--- | :--- |
| A | `anshita.in` | `<Oracle Elastic IP>` | ☁️ Proxied |
| A | `www` | `<Oracle Elastic IP>` | ☁️ Proxied |
| CNAME | `mail` | `anshita.in` | 🔘 DNS Only |

> **Important:** Proxied status hides your Oracle server's IP from attackers.

---

## Step 3: SSL/TLS Mode

1. Go to **SSL/TLS** → **Overview**
2. Select **Full (Strict)**
   - This ensures Cloudflare verifies your Let's Encrypt cert on the Oracle server
   - End-to-end encryption: Browser ↔ Cloudflare ↔ Oracle

---

## Step 4: Page Rules

Create these Page Rules (in order):

### Rule 1 — Disable Rocket Loader for site
- **URL Pattern:** `anshita.in/*`
- **Setting:** Rocket Loader → Off
- **Reason:** Rocket Loader breaks Three.js/WebGL initialization

### Rule 2 — Cache Static Assets
- **URL Pattern:** `anshita.in/static/*`
- **Settings:**
  - Cache Level: Cache Everything
  - Browser Cache TTL: 1 year
  - Edge Cache TTL: 1 month

### Rule 3 — Always Use HTTPS
- **URL Pattern:** `http://anshita.in/*`
- **Setting:** Always Use HTTPS

---

## Step 5: Additional Settings

### Security
- **Security Level:** Medium
- **Bot Fight Mode:** On (free)
- **Hotlink Protection:** On (prevents image theft)

### Speed
- **Auto Minify:** CSS ✅ | JavaScript ✅ | HTML ✅
- **Brotli:** On
- **Rocket Loader:** Off (disabled via Page Rule above)

### Caching
- **Caching Level:** Standard
- **Browser Cache TTL:** Respect Existing Headers

---

## Step 6: Verify Setup

After 5 minutes (DNS propagation):

```bash
# Check HTTPS works
curl -I https://anshita.in

# Check Cloudflare cache hit
curl -I https://anshita.in/static/core/css/style.css
# Look for: cf-cache-status: HIT (on second request)

# Check security headers
curl -I https://anshita.in | grep -i "strict-transport"
```

---

## Free Tier Limits (Cloudflare Free Plan)

| Feature | Free Limit |
| :--- | :--- |
| Bandwidth | Unlimited |
| Requests | Unlimited |
| Page Rules | 3 rules |
| Workers | 100,000 req/day |
| Rate Limiting | Not included (use Nginx) |

> With 3 Page Rules on the free plan, prioritize: (1) Rocket Loader off, (2) Static cache, (3) Always HTTPS.
