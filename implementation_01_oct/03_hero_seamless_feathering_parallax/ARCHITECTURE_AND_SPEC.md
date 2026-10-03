# 03 — HERO SEAMLESS FEATHERING & 2.5D PARALLAX

## 1. Specification & Standards
- **Design Philosophy**: Zero demarcation lines. The bridal portrait must melt seamlessly into the dark royal background with organic feathered transparency (as seen on *Demilie* and *LxL Creative*).
- **Above-The-Fold Rule**: All primary editorial copy and conversion actions (`लुकबुक` / `तारीख आरक्षित करें`) must be 100% visible on 1366x768, 1440x900, and 1920x1080 screens without requiring any initial scrolling.
- **Typography**: Cursive typography (`Bridal Couturier`) must be responsive and wrap gracefully without truncation or overflow clipping.

## 2. Technical Implementation Architecture
- **Multi-Stop Feathered Directional Mask**:
  ```css
  #heroCarousel {
    -webkit-mask-image: linear-gradient(to right, rgba(0,0,0,1) 0%, rgba(0,0,0,0.95) 45%, rgba(0,0,0,0.65) 68%, rgba(0,0,0,0.2) 84%, transparent 100%),
                        linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 85%, transparent 100%);
    -webkit-mask-composite: source-in;
    mask-composite: intersect;
  }
  ```
- **2.5D Mouse Parallax Depth**:
  - Headroom and viewport coordinate tracking tilts the bridal portrait gently on mousemove:
  ```javascript
  const tiltX = (e.clientX / window.innerWidth - 0.5) * 6;
  const tiltY = -(e.clientY / window.innerHeight - 0.5) * 6;
  heroCarousel.style.transform = `perspective(1000px) rotateY(${tiltX}deg) rotateX(${tiltY}deg)`;
  ```

## 3. Files Impacted
- `django/core/templates/core/home.html`
- `django/core/templates/core/base.html`

## 4. Verification Evidence
- Verified via Playwright: `verify_asha_full_screen.png` demonstrates smooth gradient fade-out with zero vertical lines and full CTA visibility.
