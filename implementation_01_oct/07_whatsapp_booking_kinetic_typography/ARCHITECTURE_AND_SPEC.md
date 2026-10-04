# Module 07: WhatsApp Booking CTA & Kinetic Typography

**Spec:** [SPEC-007](../../.specify/specs/SPEC-007-whatsapp-booking-cta-kinetic-typography.md)  
**Plan:** [PLAN-007](../../.specify/plans/PLAN-007-whatsapp-booking-cta-kinetic-typography.md)  
**Tasks:** [TASKS-007](../../.specify/tasks/TASKS-007-whatsapp-booking-cta-kinetic-typography.md)  
**Status:** ⏳ Pending Execution  
**Inspired by:** Stanzza.design • LxL Creative • Juan Mora

---

## What This Module Delivers

| Feature | Description |
| :--- | :--- |
| **Kinetic Oversized Headline** | `Cormorant Garamond` 96–140px Hindi tagline with character-level stagger reveal animation and scroll parallax drift |
| **Dual-Direction Marquee** | Infinite horizontal gold ticker showing 6 signature services, reverse direction on second row, pauses on hover |
| **WhatsApp FAB** | Fixed bottom-right floating action button (green pulse ring) opening pre-filled WhatsApp booking message |
| **Desktop Inline CTA** | Gold gradient "Book on WhatsApp" button inside hero CTA group (desktop only) |
| **Metric Counters** | 3 glass cards counting up: 1200+ Brides, 15 Cities, 12+ Years — triggered by IntersectionObserver |

---

## Reference Benchmarks

- **Stanzza.design** — Ultra-bold Domaine Display kinetic hero type with scroll scrub
- **LxL Creative** — Dual-direction marquee with service tags and hover pause
- **Juan Mora** — Single hero CTA with WhatsApp-like instant contact

---

## Key Technical Decisions

1. **No external CountUp.js** — pure vanilla JS with `setInterval` + `IntersectionObserver`
2. **No GSAP SplitText** (paid plugin) — custom `span`-wrapping with CSS `--i` custom property
3. **FAB positioned at `right: 88px`** (not `right: 24px`) to avoid overlap with Asha mascot toggle
4. **WhatsApp phone loaded from Django settings** — never hardcoded, change in one place

---

## Files to Create / Modify

```
django/core/templates/core/
├── base.html        ← WhatsApp FAB, marquee strip, font preload
└── home.html        ← Kinetic headline, metric counters, desktop CTA

django/core/static/core/css/
└── style.css        ← Marquee keyframes, FAB styles, counter cards, char-rise animation

anshita_project/
└── settings.py      ← WHATSAPP_PHONE setting
```

---

## Acceptance Test Checklist

- [ ] Kinetic headline characters rise in stagger sequence on first load
- [ ] Marquee scrolls continuously, reverses on second row, pauses on hover
- [ ] FAB appears after 3s delay with green pulse ring, does not overlap Asha mascot
- [ ] Click FAB → opens WhatsApp with pre-filled message
- [ ] Metric counters count from 0 when section enters viewport
- [ ] All animations disabled in `prefers-reduced-motion: reduce` mode
