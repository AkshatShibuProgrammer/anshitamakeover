# Analysis 01 — AI Concierge Overhaul

**Status:** COMPLETED
**Branch:** 20092026
**Priority:** CRITICAL

---

## 1. Problem Statement

The user reported: *"AI is answering default answers only — I don't think it is using proper Gemini AI even."*

The chatbot falls through to `fallback_chatbot()` (a hard-coded rule-based keyword matcher) when:
- `gemini_api_key.txt` does not exist, OR
- The file contains the placeholder string `YOUR_GEMINI_API_KEY_HERE`, OR
- The Gemini HTTP call throws any exception (including network timeouts).

The fallback produces stock templated responses that feel robotic and do not reflect live pricing, availability, or negotiation.

---

## 2. Current State — Code Path

```
chatbot_api() [chatbot.py:33]
  └─► reads gemini_api_key.txt [line 43-46]
       ├─ file missing / placeholder  ──► fallback_chatbot(user_msg)  [line 49]
       └─ key exists                  ──► gemini_chat(api_key, user_msg, session_id)
            └─ any Exception          ──► fallback_chatbot(user_msg)  [line 54]
```

### File: `django/gemini_api_key.txt`
- **Current:** FILE DOES NOT EXIST on this machine.
- **Effect:** Every single chat message hits the fallback silently.

### Gemini Model Used (when key is present)
- `gemini-2.5-flash` (set in `GEMINI_MODEL` env var or code default — line 67)
- System prompt is richly built with live DB pricing, negotiation guardrails, VIP codes (lines 153-179).
- History compression via `headroom` library attempted (line 85).

### Fallback Function (lines ~200-250 in chatbot.py)
- Keyword matching: "price", "bridal", "book", "appointment", etc.
- Returns canned phrases with no DB data.

---

## 3. Root Causes (in priority order)

| # | Root Cause | Impact |
|---|-----------|--------|
| 1 | `gemini_api_key.txt` missing from `django/` directory | ALL AI requests fall back |
| 2 | No visible error surfaced to user or admin when fallback triggers | Silent failure |
| 3 | `headroom` library likely not installed (optional, but causes noise if it throws) | Minor noise |
| 4 | No env-var fallback for API key (only file-based) | Fragile in cloud/Render deploys |
| 5 | `thinkingBudget: 0` in generationConfig — good for latency but may reduce quality | Minor quality |

---

## 4. Proposed Solution

### 4a. Primary Fix: Secure Key Configuration

**Option A — File (for local dev):**
Create `django/gemini_api_key.txt` with the real key.
Add to `.gitignore` so it is never committed.

**Option B — Environment Variable (for production/Render):**
Read from `os.environ.get('GEMINI_API_KEY', '')` as a priority before falling back to the file.
This is the standard approach for cloud deployments.

**Recommended: Support BOTH — env var first, file second.**

```python
# Proposed key-loading logic (replaces lines 43-46)
api_key = os.environ.get('GEMINI_API_KEY', '').strip()
if not api_key:
    key_file = Path(settings.BASE_DIR) / 'gemini_api_key.txt'
    if key_file.exists():
        api_key = key_file.read_text().strip()
```

### 4b. Admin Visibility Fix: Surface Fallback Status

When the fallback triggers, include a soft signal in the response so admin knows:
```python
# In fallback_chatbot() return value, append (only in DEBUG mode):
# [DEBUG: Gemini unavailable, fallback active]
```

Better: Add a `/api/admin/ai-status/` endpoint that returns whether Gemini is live.

### 4c. Improve Fallback Quality (interim measure)

Even if the key is missing, the fallback should pull live DB data:
- Query `MakeupPackage.objects.filter(is_active=True)` and inject top-3 prices.
- Use `SiteSettings` to get live WhatsApp number.

### 4d. Model Tuning Review

Current config: `temperature: 0.25`, `maxOutputTokens: 600`, `thinkingBudget: 0`.
- `thinkingBudget: 0` = no chain-of-thought. Good for speed, fine for conversational use.
- Temperature 0.25 = very deterministic. Could raise to 0.4 for more natural responses.
- Consider: `gemini-2.0-flash` as a cost-performance middle ground.

---

## 5. Files to Modify

| File | Change |
|------|--------|
| `django/core/views/chatbot.py` | Lines 43-54: env var priority key loading; lines ~200: fallback DB enrichment |
| `django/.gitignore` (or root) | Ensure `gemini_api_key.txt` is excluded from git |
| `django/render.yaml` | Add `GEMINI_API_KEY` as env var reference for Render cloud |
| `django/core/templates/core/home.html` | Admin panel: add AI status indicator (green/red dot) |

---

## 6. Risks

- **Secret exposure:** Key must never be committed to git. Add a pre-commit hook check.
- **Cost overrun:** With a real key, every chat message costs tokens. Rate-limit per session.
- **Timeout:** Gemini can be slow (2-5s). The current 15s timeout is safe but UX feels frozen. Add a typing indicator on the frontend.

---

## 7. Implementation Checklist

- [x] Add `gemini_api_key.txt` to `.gitignore`
- [x] Update key-loading in `chatbot.py` to check env var first
- [x] Test locally: create key file, send a real message, verify Gemini response
- [x] Enrich `fallback_chatbot()` with live DB pricing as interim safety net
- [x] Add `/api/admin/ai-status/` endpoint
- [x] Add green/red Gemini status dot in Admin Panel AI tab
- [x] Document `GEMINI_API_KEY` in `render.yaml` env section
- [x] Verify `headroom` dependency or remove gracefully

