# PLAN-007: WhatsApp Booking CTA & Kinetic Typography — Technical Blueprint

**Spec:** [SPEC-007](../specs/SPEC-007-whatsapp-booking-cta-kinetic-typography.md)  
**Status:** Active  
**Estimated Effort:** 2–3 hours

---

## 1. Files to Touch

| File | Change |
| :--- | :--- |
| `django/core/templates/core/base.html` | Add WhatsApp FAB, marquee strip, preload font links |
| `django/core/templates/core/home.html` | Add kinetic hero headline, metric counters section |
| `django/core/static/core/css/style.css` | Marquee keyframes, FAB styles, counter glass card styles |
| `django/core/settings.py` / `production.py` | Add `WHATSAPP_PHONE` setting |
| `django/core/templates/core/base.html` | GSAP SplitText-like span animation on hero tagline |

---

## 2. Architecture & DOM Design

### 2.1 WhatsApp FAB

```html
<!-- Inserted before </body> in base.html -->
<a id="whatsapp-fab" 
   href="https://wa.me/{{ settings.WHATSAPP_PHONE }}?text=..."
   class="whatsapp-fab"
   target="_blank" rel="noopener"
   aria-label="Book on WhatsApp">
  <svg><!-- WhatsApp SVG icon --></svg>
  <span class="fab-pulse-ring"></span>
</a>
```

```css
.whatsapp-fab {
  position: fixed;
  bottom: 28px; right: 88px; /* offset left of Asha mascot */
  width: 56px; height: 56px;
  background: #25D366;
  border-radius: 50%;
  z-index: 9000;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 20px rgba(37,211,102,0.45);
  animation: fab-appear 0.6s 3s both ease-out;
}
.fab-pulse-ring {
  position: absolute; inset: -6px;
  border: 2px solid rgba(37,211,102,0.6);
  border-radius: 50%;
  animation: pulse-ring 2s 3.5s infinite ease-out;
}
@keyframes pulse-ring {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(1.8); opacity: 0; }
}
```

### 2.2 Dual-Direction Marquee

```html
<div class="marquee-band" aria-hidden="true">
  <div class="marquee-track"><!-- forward items --></div>
  <div class="marquee-track marquee-reverse"><!-- reverse items --></div>
</div>
```

```css
@keyframes marquee-fwd { from { transform: translateX(0); } to { transform: translateX(-50%); } }
@keyframes marquee-rev { from { transform: translateX(-50%); } to { transform: translateX(0); } }
.marquee-track { animation: marquee-fwd 22s linear infinite; }
.marquee-reverse { animation: marquee-rev 22s linear infinite; }
.marquee-band:hover .marquee-track { animation-play-state: paused; }
```

### 2.3 Kinetic Hero Typography

```javascript
// Span-splitting for character stagger animation
function splitAndAnimate(el) {
  const chars = el.textContent.split('');
  el.innerHTML = chars.map((c, i) =>
    `<span class="char" style="--i:${i}">${c === ' ' ? '&nbsp;' : c}</span>`
  ).join('');
}
// CSS: .char { display: inline-block; animation: char-rise 0.8s calc(var(--i)*0.04s) both; }
```

### 2.4 CountUp Metric Counters

```javascript
function countUp(el, target, suffix) {
  const obs = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return;
    obs.disconnect();
    let n = 0;
    const step = Math.ceil(target / 60);
    const timer = setInterval(() => {
      n = Math.min(n + step, target);
      el.textContent = n + suffix;
      if (n >= target) clearInterval(timer);
    }, 16);
  }, { threshold: 0.4 });
  obs.observe(el);
}
```

---

## 3. Phase Sequence

| Phase | Task | Duration |
| :--- | :--- | :--- |
| P7.1 | Font preload + kinetic hero tagline span-split | 30 min |
| P7.2 | Dual-direction service marquee strip | 30 min |
| P7.3 | WhatsApp FAB + pulse ring + UTM link | 30 min |
| P7.4 | Metric counter glass cards (IntersectionObserver) | 30 min |
| P7.5 | Django `WHATSAPP_PHONE` setting + template tag | 20 min |
| P7.6 | Visual browser verification | 20 min |

---

## 4. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| FAB overlaps Asha mascot on mobile | Position FAB `right: 88px` (Asha is at `right: 24px`) |
| CLS from font loading | `font-display: swap` + preload in `<head>` |
| Marquee causes layout reflow | Use `will-change: transform` + `overflow: hidden` container |
