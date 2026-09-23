# Analysis 04 — Security Audit (Veracode-Style)

**Status:** PENDING IMPLEMENTATION
**Branch:** 20092026
**Priority:** HIGH

---

## 1. Scope

A systematic security review of the Anshita Makeover Django application modeled after Veracode's CWE-based vulnerability categories. Covers: injection, authentication, authorization, sensitive data exposure, XSS, CSRF, insecure configuration, and dependency risks.

---

## 2. Attack Surface Map

```
Public Internet
  |
  |-- GET/POST /                          home.html
  |-- GET /api/chat/                      chatbot_api()
  |-- POST /api/admin/ai-command/         admin_ai_command()  [login_required]
  |-- POST /api/admin/*/                  various admin endpoints [login_required?]
  |-- POST /api/coupon/save/              coupon views
  |-- POST /api/media/*/                  media management
  |-- POST /login/  /logout/             auth views
  |-- /django-admin/                      Django built-in admin
  |-- /static/*                           Static files
  |-- /media/*                            User-uploaded files (CRITICAL)
```

---

## 3. Vulnerability Findings

### 3.1 CWE-89: SQL Injection
**Risk: LOW** (Django ORM used throughout)
- All queries use Django ORM: `MakeupPackage.objects.filter(...)`, not raw SQL.
- Exception: Check for any `RawQuerySet` or `.raw()` calls.
- Action: `grep -r "\.raw(" django/` — confirm none present.
- If any exist, parameterize immediately.

### 3.2 CWE-79: Cross-Site Scripting (XSS)
**Risk: MEDIUM**
- Django templates auto-escape by default (`{{ var }}` is safe).
- Risk points:
  - `{{ pkg.features|safe }}` — if `|safe` is used anywhere on user-input fields, XSS is possible.
  - Admin-entered content (package names, taglines) rendered with `|safe`.
  - `MakeupPackage.features` is staff-entered but verify it is not rendered with `|safe`.
- Action: Search `grep -n "|safe" django/core/templates/` — audit each use.
- JavaScript `innerHTML` assignments using server data are dangerous.
  - Search: `innerHTML` in home.html JS sections — any dynamic render of DB strings.

### 3.3 CWE-352: CSRF
**Risk: MEDIUM-HIGH**
- `chatbot_api()` has `@csrf_exempt` (line 31) — INTENTIONAL for public API but means no CSRF protection.
  - Acceptable for a public read endpoint, but verify it cannot mutate sensitive data.
  - Currently: saves `ChatMessage` (low risk, public data).
- All admin POST endpoints must NOT be csrf_exempt.
  - Action: Audit every `@csrf_exempt` decorator usage.
  - Expected locations: `chatbot_api`, possibly some media endpoints.
- The admin panel JS should send the `X-CSRFToken` header on all POST requests.
  - Verify `getCookie('csrftoken')` is used in every `fetch()` POST in `home.html`.

### 3.4 CWE-285: Improper Authorization (IDOR)
**Risk: MEDIUM**
- `/api/admin/ai-command/` uses `@login_required` — good.
- Risk: Is `admin_required` decorator used (from `common.py`) or just `login_required`?
  - `login_required` only checks authentication, NOT staff/superuser status.
  - A registered non-staff user could call admin APIs if they have an account.
- Action: Replace `@login_required` with `@staff_member_required` on ALL admin endpoints, or verify the custom `admin_required` decorator checks `user.is_staff`.
- Check `common.py` `admin_required` implementation:
  ```python
  # Expected safe pattern:
  def admin_required(view_func):
      def wrapper(request, *args, **kwargs):
          if not request.user.is_authenticated or not request.user.is_staff:
              return JsonResponse({'error': 'Unauthorized'}, status=403)
          return view_func(request, *args, **kwargs)
      return wrapper
  ```

### 3.5 CWE-200: Sensitive Data Exposure
**Risk: HIGH**
- `gemini_api_key.txt` in the Django project root — if this is committed to git, the API key is exposed.
  - Verify: `git log --all --full-history -- "django/gemini_api_key.txt"` — has it ever been committed?
  - Add to `.gitignore` immediately.
- Django `SECRET_KEY` — stored in `settings.py` directly or via env var?
  - Check `anshita_project/settings.py` — must use `os.environ.get('SECRET_KEY')`.
- Database credentials — SQLite on local is fine, but Render PostgreSQL credentials must be via env var.
- Debug mode — `DEBUG=True` in production exposes full stack traces with local file paths.
  - Verify `DEBUG = os.environ.get('DEBUG', 'False') == 'True'` in settings.

### 3.6 CWE-434: Unrestricted File Upload
**Risk: HIGH**
- `MediaItem.image_file` uses `ImageField(upload_to='media_uploads/images/')`.
- `MediaItem.video_file` uses `FileField(upload_to='media_uploads/videos/')`.
- Django `ImageField` validates that the file is a valid image (via Pillow) — good for images.
- `FileField` (video) does NOT validate content type — a malicious file could be uploaded.
- Risk: If `/media/*` files are served directly by Nginx/Django without content-type validation, stored XSS or malicious file execution is possible.
- Action:
  - Add file extension whitelist validation in the view handling video uploads.
  - Ensure media files are served with `Content-Disposition: attachment` or at minimum correct MIME types.
  - Never execute uploaded files on the server.

### 3.7 CWE-916: Weak Password / Authentication
**Risk: LOW-MEDIUM**
- Django's default `AbstractUser` password hashing (PBKDF2-SHA256) is strong.
- Check: Is there a minimum password length requirement in the signup form?
- Check: Are there any hardcoded admin passwords in code or fixtures?
  - Action: `grep -r "password" django/` — filter for hardcoded strings.
- Check: Is `SECURE_SSL_REDIRECT` set to True in production settings?

### 3.8 CWE-1021: Clickjacking
**Risk: LOW**
- Django provides `X-Frame-Options` middleware (`django.middleware.clickjacking.XFrameOptionsMiddleware`).
- Verify it is in `MIDDLEWARE` in `settings.py`.
- Recommended value: `DENY` or `SAMEORIGIN`.

### 3.9 Dependency Vulnerabilities
**Risk: UNKNOWN — needs scan**
- `requirements.txt` lists: Django, requests, Pillow, etc.
- Action: Run `pip-audit` or `safety check` against `requirements.txt`.
- Pin all dependency versions to avoid supply-chain attacks.

### 3.10 Information Disclosure via Error Pages
**Risk: MEDIUM**
- If `DEBUG=True` in production, Django shows full stack traces including file paths, settings, and DB queries.
- Custom `404.html` and `500.html` templates should be created if not present.
- Action: Confirm `DEBUG=False` in production, and verify custom error pages exist.

---

## 4. Priority Remediation Matrix

| CWE | Severity | Effort | Fix First? |
|-----|----------|--------|-----------|
| Sensitive Data (API key, SECRET_KEY) | CRITICAL | Low | YES |
| Improper Authorization (login vs staff) | HIGH | Low | YES |
| Unrestricted File Upload | HIGH | Medium | YES |
| CSRF on admin endpoints | MEDIUM | Low | YES |
| XSS via `|safe` filter | MEDIUM | Low | YES |
| Debug mode in production | MEDIUM | Low | YES |
| Clickjacking (X-Frame-Options) | LOW | Low | After above |
| Dependency audit | UNKNOWN | Low | After above |
| Password policy | LOW | Medium | Later |

---

## 5. Files to Audit

| File | What to Check |
|------|--------------|
| `django/anshita_project/settings.py` | DEBUG, SECRET_KEY, ALLOWED_HOSTS, MIDDLEWARE, SECURE_* settings |
| `django/core/views/common.py` | `admin_required` decorator — does it check `is_staff`? |
| `django/core/views/chatbot.py` | `@csrf_exempt` uses — are they all necessary? |
| `django/core/views/media.py` | File upload validation for video files |
| `django/core/templates/core/home.html` | `|safe` filter uses, `innerHTML` assignments |
| `.gitignore` | Is `gemini_api_key.txt` listed? |
| `requirements.txt` | Version pins and known vulnerabilities |
| `django/core/urls.py` | Are any admin URLs accidentally public? |

---

## 6. Implementation Checklist

- [ ] Add `gemini_api_key.txt` to `.gitignore`; verify it was never committed to git
- [ ] Audit `settings.py` — SECRET_KEY from env, DEBUG from env, ALLOWED_HOSTS locked
- [ ] Audit `admin_required` in `common.py` — must check `is_staff` not just `is_authenticated`
- [ ] Apply `admin_required` (not just `login_required`) to ALL admin-facing views
- [ ] Search for `@csrf_exempt` in all views — document and justify each use
- [ ] Search for `|safe` in all templates — remove or whitelist-sanitize each
- [ ] Search for `innerHTML` in JS — replace with `textContent` where possible
- [ ] Add file type whitelist validation to video upload handler
- [ ] Enable `XFrameOptionsMiddleware` and set `X_FRAME_OPTIONS = 'DENY'`
- [ ] Enable `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` in production settings
- [ ] Create `templates/404.html` and `templates/500.html` if missing
- [ ] Run `pip-audit` on `requirements.txt` and fix any flagged packages
- [ ] Add pre-commit hook to block commits of files matching `*api_key*` or `*secret*`
