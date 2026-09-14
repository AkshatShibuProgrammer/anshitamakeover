# 💄 Anshita Makeover — Full Stack Web Application

> A professional beauty & makeup studio management system built with Django, featuring animated UI, AI chatbot, coupon management, event packages, and an artist portfolio — designed for **Anshita Makeover, Bhopal, Madhya Pradesh**.

---

## 📌 Table of Contents

1. [Why We Built This](#-why-we-built-this)
2. [What We Are Trying to Achieve](#-what-we-are-trying-to-achieve)
3. [What We Built](#-what-we-built)
4. [Business Requirements](#-business-requirements)
5. [Functional Requirements](#-functional-requirements)
6. [Non-Functional Requirements](#-non-functional-requirements)
7. [Tech Stack](#-tech-stack)
8. [Project Structure](#-project-structure)
9. [How to Run](#-how-to-run)
10. [Admin Credentials](#-admin-credentials)
11. [Artists & Pricing](#-artists--pricing)
12. [Coupon Logic](#-coupon-logic)
13. [Chatbot Setup](#-chatbot-setup)
14. [Future Roadmap](#-future-roadmap)

---

## 💡 Why We Built This

Anshita Makeover is a well-known professional makeup studio in Bhopal, MP, run by **Anshita** — a bridal makeup artist with 8+ years of experience and 500+ happy brides.

The business was growing rapidly but lacked:
- A **professional digital presence** to attract clients online
- A way to **showcase artists, services and packages** clearly
- A system to **manage promotional coupons** without technical help
- A **learning academy section** to promote their makeup courses
- An **event management portfolio** covering photography packages
- A **24/7 chatbot** to handle client queries automatically on the website
- A **WhatsApp-first booking experience** that is natural for Indian users

This app was created to solve all of the above — giving Anshita Makeover a world-class web presence matching international makeup artist websites (inspired by Eva García, Barcelona), while staying rooted in the Indian bridal market.

---

## 🎯 What We Are Trying to Achieve

| Goal | Description |
|---|---|
| 🌐 **Online Presence** | A stunning animated website that instantly communicates trust & luxury |
| 📱 **Mobile First** | 95%+ Indian users visit via mobile — fully responsive with bottom nav bar |
| 💄 **Showcase Services** | Display makeup, hair, nails, beauty services with artist-wise assignment |
| 🎓 **Academy Growth** | Promote makeup artist courses with full fee breakdown & WhatsApp enquiry |
| 🏷️ **Smart Coupons** | Auto-rotating monthly coupon system controlled by admin — no coding needed |
| 📸 **Gallery & Portfolio** | Show real bridal work, linked to Instagram |
| 🤖 **AI Chatbot** | Gemini-powered chatbot that answers in Hinglish — reduces manual WhatsApp load |
| 🎊 **Event Management** | Sell photography + event packages with custom admin-created combos |
| 🔐 **Admin Control** | Non-technical admin (Akshat) can manage prices, coupons & packages from a simple panel |
| 🌍 **Multilingual** | English / Hinglish / Hindi toggle for broader reach |

---

## 🏗️ What We Built

### Pages
| Page | URL | Description |
|---|---|---|
| Home | `/` | Hero, Services, Artists, Packages, Events, Gallery, About, Academy CTA |
| Academy | `/academy/` | Standalone courses page with fee breakdown, modules, coupon display |
| Admin Login | `/admin-login/` | Custom branded admin login (hidden at footer) |
| Django Admin | `/django-admin/` | Full backend CMS for all data management |

### Features Built
- ✅ Animated hero section (particle canvas, floating photo, scroll reveal)
- ✅ Custom gold cursor with ring follow effect
- ✅ Circular scroll progress indicator
- ✅ Preloader with spinning logo animation
- ✅ Letter-by-letter nav hover animation
- ✅ Coupon banner with shimmer, timer countdown, copy-to-clipboard
- ✅ Auto coupon rotation by date (Days 1–10, 11–20, 21–31)
- ✅ Admin floating panel (coupon, prices, event packages)
- ✅ 5 Artists configured with specialities and pricing
- ✅ Professional Makeup Artist Program with 6 modules
- ✅ 2 Photography packages (₹1.2L Premium, ₹90K Standard)
- ✅ Admin can create custom event + makeup combo packages
- ✅ Gemini AI chatbot (fallback rule-based if no API key)
- ✅ WhatsApp deep link (auto opens chat with 7879223442)
- ✅ Gallery with filter by category (Bridal, Nails, Hair, Party etc.)
- ✅ Mobile bottom nav bar
- ✅ Language switcher (English / Hinglish / Hindi)
- ✅ Count-up statistics animation
- ✅ Django ORM database with full admin panel
- ✅ Password reset via email (Django built-in)

---

## 📊 Business Requirements

| BR# | Requirement | Priority |
|---|---|---|
| BR-01 | Showcase Anshita and all 5 artists (Anshita, Shristee, Priya, Tejal, Sindhu) with their specialities | High |
| BR-02 | Tejal's makeup package must be priced at ₹45,000; all others at ₹35,000 | High |
| BR-03 | Nail art is exclusively handled by Shristee | High |
| BR-04 | Hair services handled by Anshita, Sindhu, Shristee and Priya | High |
| BR-05 | Academy registration fee is ₹5,000 | High |
| BR-06 | Professional Makeup Artist Program: 4 weeks, 3hr/day, 84 total hours, ₹35,400 incl. GST | High |
| BR-07 | Coupon system: Days 1–10 = 30% off, Days 11–20 = 50% off, Days 21–31 = 10% off | High |
| BR-08 | Admin (login: akshat / Anshita@2026) can override coupons manually at any time | High |
| BR-09 | Admin can create custom event/photography/makeup combo packages | High |
| BR-10 | Photography Premium package = ₹1,20,000 with all features | High |
| BR-11 | Photography Standard package = ₹90,000 | High |
| BR-12 | WhatsApp number 7879223442 must auto-open chat on click | High |
| BR-13 | Instagram: @anshitamakeover21 must be linked for gallery | Medium |
| BR-14 | Academy must be a separate page, not embedded in home | High |
| BR-15 | Admin can control price of each service/artist/course from panel | High |
| BR-16 | Password reset using registered email ID | Medium |
| BR-17 | Language toggle: English, Hinglish (default), Hindi | Medium |
| BR-18 | AI chatbot must answer queries in Hinglish naturally | Medium |
| BR-19 | Gallery must have category filters | Low |
| BR-20 | Admin panel must be simple — usable in English or Hinglish | High |

---

## ✅ Functional Requirements

### F1 — User-Facing Website
- **F1.1** Display hero section with Anshita's photo, tagline, and CTA buttons
- **F1.2** Services section listing Makeup, Hair, Nails, Beauty, Bridal Packages, Event Management — each with relevant artist chips
- **F1.3** Artists section showing all 5 artists with photo placeholder, specialities, and bridal pricing
- **F1.4** Wedding Makeup Packages section with 3 default packages + custom packages created by admin
- **F1.5** Event Management section with Photography Premium (₹1.2L), Photography Standard (₹90K), and admin-created custom combos
- **F1.6** Gallery section with filter by category (Bridal, Engagement, Hair, Nails, Party, Beauty)
- **F1.7** About section with Anshita's bio and animated count-up statistics
- **F1.8** Academy CTA banner linking to Academy page
- **F1.9** Footer with social links, nav links, and admin login button

### F2 — Academy Page
- **F2.1** Standalone page at `/academy/` separate from homepage
- **F2.2** Registration fee banner (₹5,000)
- **F2.3** Course cards with duration, hours/day, total hours, module count
- **F2.4** Fee breakdown table: Course Fee + GST + Coupon Discount = Total Payable
- **F2.5** Expandable curriculum list with module-by-module breakdown
- **F2.6** WhatsApp Enquiry and Enrol Now CTA buttons
- **F2.7** Batch start announcement banner

### F3 — Coupon System
- **F3.1** Auto-detect date and apply correct coupon (30%/50%/10%)
- **F3.2** Show coupon banner with discount badge, label, code, and countdown timer
- **F3.3** Copy coupon code on click
- **F3.4** Admin can manually override coupon from floating panel
- **F3.5** Admin can create completely custom coupons with any code, discount %, and label
- **F3.6** Admin can hide/remove the coupon banner entirely

### F4 — Admin Panel
- **F4.1** Admin login at `/admin-login/` with username `akshat` and password `Anshita@2026`
- **F4.2** Floating side panel (visible only when logged in) with tabs: Coupon, Prices, Events, Status
- **F4.3** Coupon tab: select preset coupons or create custom; toggle auto-date mode
- **F4.4** Prices tab: edit artist fees, course fees, nail art prices, photography prices
- **F4.5** Events tab: create, view, delete custom event/combo packages
- **F4.6** Status tab: view active coupon, logged-in user, quick links
- **F4.7** Full Django Admin at `/django-admin/` for complete data management
- **F4.8** Password reset via email from login page

### F5 — AI Chatbot
- **F5.1** Floating chatbot button (gold, bottom-left)
- **F5.2** Chat window with bot identity as "Anshita AI 💄"
- **F5.3** API key loaded from `gemini_api_key.txt` — no hardcoding
- **F5.4** Gemini 1.5 Flash model with Hinglish system prompt
- **F5.5** Fallback rule-based chatbot if API key not set
- **F5.6** Chat history stored in database (ChatMessage model)
- **F5.7** Typing indicator animation

### F6 — WhatsApp Integration
- **F6.1** Every CTA button opens WhatsApp with pre-filled message
- **F6.2** Number: 7879223442 (stored in SiteSettings, editable by admin)
- **F6.3** Mobile bottom bar has direct WhatsApp button
- **F6.4** Different messages per action (book, enquire, enrol, custom quote etc.)

### F7 — Language
- **F7.1** Cookie-based language preference (English / Hinglish / Hindi)
- **F7.2** Default language: Hinglish
- **F7.3** Language buttons in top navigation
- **F7.4** Content dynamically renders in selected language

---

## 🔒 Non-Functional Requirements

### Performance
- **NF-01** Page load under 3 seconds on mobile 4G connection
- **NF-02** Particle animation capped at 90 particles — no performance degradation
- **NF-03** Images lazy-loaded; placeholders shown until photos added

### Security
- **NF-04** Admin panel only visible and accessible when user is logged in (Django auth)
- **NF-05** CSRF protection on all POST endpoints
- **NF-06** Gemini API key stored in file, never in source code or frontend
- **NF-07** Default admin password enforces uppercase, symbol, and number
- **NF-08** Password reset flow uses Django's secure token-based email system

### Usability
- **NF-09** Fully mobile responsive — tested for 320px to 1920px viewport widths
- **NF-10** Mobile bottom navigation bar for thumb-friendly navigation
- **NF-11** All CTA buttons minimum 44px touch target
- **NF-12** Admin panel simple enough for non-technical users — all in plain English/Hinglish
- **NF-13** Chatbot fallback ensures the bot always responds even without API key

### Accessibility
- **NF-14** All images have alt text
- **NF-15** Color contrast ratio meets WCAG AA for primary text
- **NF-16** Hamburger menu accessible with keyboard

### Maintainability
- **NF-17** All site data (artists, courses, packages, prices, gallery) managed via Django Admin
- **NF-18** No price or coupon hardcoded — all come from database
- **NF-19** New artists, packages, and courses can be added without code changes
- **NF-20** Gemini API key swappable by editing a single text file

### Scalability
- **NF-21** SQLite for development; can be switched to PostgreSQL for production
- **NF-22** Static files served via Django in dev; can use Whitenoise/CDN in production
- **NF-23** Architecture supports adding new pages (e.g., Blog, Testimonials) easily

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13 + Django 6.1 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Vanilla HTML5, CSS3, JavaScript (no framework — fast load) |
| AI Chatbot | Google Gemini 1.5 Flash via `google-generativeai` |
| Animations | CSS keyframes, Canvas API, Intersection Observer |
| Hosting (dev) | Django dev server on `0.0.0.0:3001` |
| Media | Django media files + Pillow |
| Auth | Django built-in auth + custom admin login UI |

---

## 📁 Project Structure

```
anshita_project/
│
├── manage.py                    # Django management entry point
├── seed_data.py                 # Initial data seeder script
├── gemini_api_key.txt           # 🔑 Put your Gemini API key here
├── db.sqlite3                   # SQLite database
├── README.md                    # This file
├── PROMPT.md                    # AI agent prompt for Antigravity
│
├── anshita_project/             # Django project settings
│   ├── settings.py              # All configuration
│   ├── urls.py                  # Root URL routing
│   └── wsgi.py
│
├── core/                        # Main Django app
│   ├── models.py                # All database models
│   ├── views.py                 # All view logic + chatbot + admin APIs
│   ├── urls.py                  # App URL patterns
│   ├── admin.py                 # Django admin registrations
│   ├── middleware.py            # CORS + X-Frame headers
│   ├── templatetags/
│   │   └── core_tags.py         # Custom template filters
│   ├── templates/core/
│   │   ├── base.html            # Master template (nav, footer, chatbot, cursor)
│   │   ├── home.html            # Homepage
│   │   ├── academy.html         # Academy page
│   │   └── admin_login.html     # Custom admin login
│   └── static/core/
│       └── images/
│           └── logo.jpeg        # Anshita Makeover logo
│
└── media/                       # Uploaded files (artist photos, gallery)
    ├── artists/
    └── gallery/
```

---

## ▶️ How to Run

### Prerequisites
```bash
Python 3.10+
pip
```

### Step 1 — Install dependencies
```bash
pip install django pillow google-generativeai
```

### Step 2 — Setup database
```bash
cd anshita_project
python manage.py migrate
```

### Step 3 — Seed initial data (first time only)
```bash
python seed_data.py
```
*(Or `python manage.py shell < seed_data.py`)*

### Step 4 — Add Gemini API Key
Open `gemini_api_key.txt` and replace:
```
YOUR_GEMINI_API_KEY_HERE
```
with your actual Google AI Studio key from: https://aistudio.google.com/app/apikey

### Step 5 — Run the server
```bash
python manage.py runserver 0.0.0.0:3001
```

### Step 6 — Open in browser
```
http://localhost:3001/
```

### Admin Panel
```
URL:      http://localhost:3001/admin-login/
Username: akshat
Password: Anshita@2026
```

---

## 🔐 Admin Credentials

| Field | Value |
|---|---|
| Username | `akshat` |
| Password | `Anshita@2026` |
| Admin URL | `/admin-login/` (custom) or `/django-admin/` (full) |
| Password Reset | `/django-admin/password_reset/` |

---

## 👩🎨 Artists & Pricing

| Artist | Makeup | Hair | Nails | Beauty | Bridal Fee |
|---|---|---|---|---|---|
| **Anshita** | ✅ | ✅ | — | ✅ | ₹35,000 |
| **Shristee** | ✅ | ✅ | ✅ | — | ₹35,000 |
| **Priya** | ✅ | ✅ | — | — | ₹35,000 |
| **Tejal** | ✅ | — | — | — | **₹45,000** |
| **Sindhu** | — | ✅ | — | — | — |

---

## 🏷️ Coupon Logic

| Days of Month | Coupon Code | Discount | Label |
|---|---|---|---|
| 1 – 10 | `GLAMOUR30` | 30% OFF | Start of Month Special |
| 11 – 20 | `GLAM50` | 50% OFF | Mid-Month Dhamaka |
| 21 – 31 | `ANSHITA10` | 10% OFF | Month End Offer |

- Auto-applies based on today's date
- Admin can **override** or **create custom coupon** anytime
- Admin can **completely hide** the banner

---

## 🤖 Chatbot Setup

1. Get a free API key from: https://aistudio.google.com/app/apikey
2. Open `anshita_project/gemini_api_key.txt`
3. Replace `YOUR_GEMINI_API_KEY_HERE` with your key
4. Restart the server — chatbot will now use Gemini AI

**Without API key:** A smart rule-based fallback chatbot handles common queries (bridal pricing, artists, academy, coupons, location, WhatsApp).

---

## 🔮 Future Roadmap

| Feature | Priority |
|---|---|
| Real gallery photos from Anshita's PicsArt-edited images | High |
| Artist profile photos (dark background, golden glow) | High |
| Instagram embed widget (Elfsight or SnapWidget) | Medium |
| SMS/Email booking confirmation | Medium |
| Online booking calendar with slot management | Medium |
| Customer testimonials & reviews section | Medium |
| Blog / Tips section for SEO | Low |
| Deploy to PythonAnywhere or VPS | High |
| Google Analytics integration | Low |
| Referral program for students | Low |

---

## 📞 Contact

- **WhatsApp:** [7879223442](https://wa.me/917879223442)
- **Instagram:** [@anshitamakeover21](https://www.instagram.com/anshitamakeover21/)
- **Location:** Bhopal, Madhya Pradesh, India

---

*Built with ❤️ for Anshita Makeover — Bhopal's finest bridal makeup studio*
