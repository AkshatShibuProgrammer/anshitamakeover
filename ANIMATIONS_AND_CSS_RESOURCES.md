# 🎨 Curated Design, Animation & CSS Resource Directory
> **Project:** Anshita Makeover — India's Premier Bridal Couture, Hair Artistry & Luxury Studio  
> **Purpose:** Reference manual of trusted libraries, CDN endpoints, interactive inspiration sources, and high-performance animation assets used across the web app.

---

## 1. ⚡ Live Libraries & CDNs Currently Integrated in the App

These scripts and stylesheets are actively powering the 3D graphics, motion choreography, and layout behavior in `django/core/templates/core/base.html` and `django/core/static/core/css/animations.css`:

| Library / Resource | Version / Source | CDN URL / Import Link | Used For |
| :--- | :--- | :--- | :--- |
| **Three.js** | `r128` | `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js` | WebGL luxury gold particle ripple background, floating ambient dust, and interactive mouse trails on `#bg-canvas`. |
| **GSAP (GreenSock)** | `3.12.5` | `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js` | High-precision cinematic timeline choreography, curtain splitting, and staggered typography reveals. |
| **Headroom.js** | `0.12.0` | `https://cdnjs.cloudflare.com/ajax/libs/headroom/0.12.0/headroom.min.js` | Smart floating navigation header auto-hide on downward scroll and smooth reveal on upward swipe. |
| **Google Fonts** | `Cinzel` & `Montserrat` / `Outfit` | `https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Outfit:wght@300;400;600;700&display=swap` | Luxury serif headline hierarchy for royal Indian bridal couture paired with ultra-clean modern sans body type. |
| **Custom GPU Animations** | Internal | `django/core/static/core/css/animations.css` | Zero-layout-thrashing metallic gold shimmer sweeps, couture radial pulse glows, hardware-accelerated split reveals, and velvet curtain transitions. |

---

## 2. 🏛️ Premier Luxury Editorial Design & Inspiration Benchmarks

Websites analyzed and used as benchmarks for Anshita Makeover's haute couture aesthetics, transitions, and user experience:

- **[Evagher (evagher.com)](https://evagher.com/en)**  
  *Benchmark for:* Dual-curtain entrance split, monogram stroke-draw reveals, smooth scroll physics, letter-by-letter stagger animations, and luxury dark/gold mood.
- **[Awwwards (awwwards.com)](https://www.awwwards.com/)**  
  *Benchmark for:* Cutting-edge WebGL interactions, creative direction, luxury e-commerce storytelling, and micro-interactions.
- **[FWA (thefwa.com)](https://thefwa.com/)**  
  *Benchmark for:* State-of-the-art interactive digital experiences, 3D WebGL showcases, and immersive web art.
- **[Godly Website Inspiration (godly.website)](https://godly.website/)**  
  *Benchmark for:* Ultra-clean, modern luxury layouts, editorial typography hierarchies, and subtle cursor dynamics.
- **[Sabyasachi Official (sabyasachi.com)](https://www.sabyasachi.com/)**  
  *Benchmark for:* Heritage Indian royal bridal aesthetics, deep velvet maroon and warm antique gold palettes, vintage crest typography.

---

## 3. 🎬 Top Animation & Motion Libraries for Future Upgrades

Recommended drop-in libraries for expanding animations across bridal looks, reels, and lookbooks:

### A. Physics & Smooth Scrolling
- **[Lenis by Studio Freight (darkroom.engineering/lenis)](https://github.com/darkroomengineering/lenis)**  
  *Why:* The industry-standard lightweight smooth scroll library (~3KB) that works flawlessly with GSAP ScrollTrigger and CSS sticky headers without hijacking native accessibility.  
  *CDN:* `https://unpkg.com/lenis@1.1.18/dist/lenis.min.js`
- **[GSAP ScrollTrigger (greensock.com/scrolltrigger)](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)**  
  *Why:* Pinning sections, horizontal gallery scroll (ideal for the 6 bridal looks), and scroll-tied scrubbed animations.  
  *CDN:* `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js`

### B. Micro-Animations & Sliders
- **[Swiper.js (swiperjs.com)](https://swiperjs.com/)**  
  *Why:* The gold standard mobile-touch slider with 3D Coverflow, Cube, and Fade effects. Perfect for Instagram Reel showcases and bridal before/after slider cards.  
  *CDN:* `https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js` + `swiper-bundle.min.css`
- **[Animate.css (animate.style)](https://animate.style/)**  
  *Why:* Instant plug-and-play CSS animations (`fadeInUp`, `pulse`, `zoomIn`) for rapid UI feedback and modal pops.  
  *CDN:* `https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css`
- **[AOS - Animate On Scroll (michalsnik.github.io/aos)](https://michalsnik.github.io/aos/)**  
  *Why:* Lightweight declarative data-attribute scroll reveals (`data-aos="fade-up"`).  
  *CDN:* `https://unpkg.com/aos@2.3.1/dist/aos.js` + `aos.css`

### C. Vector & 3D Interactive Graphics
- **[Lottie / DotLottie (lottiefiles.com)](https://lottiefiles.com/)**  
  *Why:* Vector JSON animations for sparkling jewel icons, celebration confetti, checkmark booking confirmations, and ring icons.  
  *CDN:* `https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js`
- **[Curtains.js / OGL](https://www.curtainsjs.com/)**  
  *Why:* WebGL image displacement effects, water ripple distortion on bridal portrait hover, and silk cloth waving shaders.

---

## 4. 🚀 Modern Creative Component Libraries & AI-Native UI Engines

Specialized creative engineering resources and copy-paste component engines for state-of-the-art interactive effects:

- **[Lightswind UI (lightswind.com)](https://lightswind.com/)**  
  *What it is:* An AI-native, CLI-first component library with built-in WebGL/3D effects, glassmorphic surfaces, and MCP (Model Context Protocol) support for AI coding agents.  
  *How Anshita Studio uses it:* Perfect for grabbing WebGL card hover shaders, ambient light reflections, and luminous gold borders.
- **[Rolling Numbers by Kit Langton (rolling.kitlangton.dev)](https://rolling.kitlangton.dev/)**  
  *What it is:* A framework-independent, interruptible rolling counter / odometer animation engine for numbers.  
  *How Anshita Studio uses it:* Ideal for the **Royal Price Calculator**, package savings counter (`₹58,000` scrolling to `₹45,000`), client review stats (`500+ Brides Blessed`), and live dynamic quotes.
- **[GetLayers AI (getlayers.ai)](https://getlayers.ai/)**  
  *What it is:* A curated library of cinematic web layouts, 3D scenes, and camera-guided prompt architectures.  
  *How Anshita Studio uses it:* Benchmark for luxury Indian wedding editorial art direction, full-bleed hero compositions, and high-fashion lighting guides.
- **[Fancy Components (fancycomponents.dev)](https://fancycomponents.dev/)**  
  *What it is:* Creative micro-interactions library with magnetic hover fields, physics-based buttons, liquid glass surfaces, and kinetic text reveals.  
  *How Anshita Studio uses it:* The primary inspiration for our **Liquid Glass Haute Couture Buttons** and magnetic floating CTAs.
- **[Scrolltide (scrolltide.co)](https://scrolltide.co/)**  
  *What it is:* A premier curated repository of cinematic, scroll-driven website templates, prompts, and motion architectures built for "movie-like" web experiences (Framer Motion, GSAP, WebGL).  
  *How Anshita Studio uses it:* Provides the blueprint for scroll-tied scrubbed reveals, 3D card tilt physics, cinematic full-bleed image zoom reveals, and luxury editorial transitions.

---

## 5. 💎 Ready-to-Use Haute Couture UI Patterns (Now in `animations.css`)

We have adapted the best concepts from these libraries into native vanilla CSS/JS so they run with **zero extra dependencies**:

### A. Liquid Glass Haute Couture Button (`.btn-liquid-glass`)
Inspired by *Fancy Components* and *Lightswind*:
- Multi-layer frosted glass background (`backdrop-filter: blur(16px) saturate(180%)`)
- Antique gold border luminance (`border: 1px solid rgba(212, 175, 55, 0.35)`)
- Dynamic 120-degree light refraction sweep on hover
- Inset specular highlight along the top bevel

```html
<!-- Example Usage in Templates -->
<a href="https://wa.me/{{ whatsapp }}" class="btn-liquid-glass">
  <span>Reserve Royal Bridal Suite</span>
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M5 12h14M12 5l7 7-7 7"/>
  </svg>
</a>
```

### B. Cinematic Scroll-Driven Revelations (Inspired by `scrolltide.co`)
Three high-impact animations adapted from Scrolltide's movie-like aesthetic:
1. **Cinematic Hero Image Slow-Zoom**: As user scrolls through the hero lookbook, images subtly scale (`scale(1.0) -> scale(1.08)`) with parallax depth.
2. **3D Card Perspective Tilt**: Bridal service cards subtly tilt toward the user's cursor on hover (`perspective: 1000px`, `rotateX/Y`), giving the feel of a heavy embossed royal invitation card.
3. **Scroll-Progress Golden Line**: A continuous 2px warm gold gradient bar at the top of the viewport indicating the bride's journey through the page.

### C. Rolling Odometer Prices (Inspired by `rolling.kitlangton.dev`)
Smoothly rolls numbers when seasonal coupons or package bundles are applied without page jumping. Uses CSS vertical translate on `.rolling-digit-strip`.

---

## 6. 🧰 CSS Generators & Precision Styling Tools

Essential web utilities to quickly prototype and extract luxury CSS properties:

- **Glassmorphism & Frosted Glass:**  
  *URL:* [hype4.academy/tools/glassmorphism-generator](https://hype4.academy/tools/glassmorphism-generator)  
  *Utility:* Generates accurate backdrop-filter blur, border luminescence, and alpha-layered dark card backgrounds.
- **Cubic Bezier Easing Playground:**  
  *URL:* [cubic-bezier.com](https://cubic-bezier.com/)  
  *Utility:* Designing custom luxury easing curves (e.g. `cubic-bezier(0.16, 1, 0.3, 1)` for snappy yet silky reveals).
- **CSS Gradient Crafting:**  
  *URL:* [cssgradient.io](https://cssgradient.io/)  
  *Utility:* Crafting multi-stop metallic gold gradients (`#D4AF37` → `#F5E296` → `#9A7B1C`).
- **Shadow Palette & Layering:**  
  *URL:* [shadows.brumm.af](https://shadows.brumm.af/)  
  *Utility:* Multi-layer diffused box shadows for high-end floating cards without harsh edges.
- **CSS Clip-Path Maker:**  
  *URL:* [bennettfeely.com/clippy](https://bennettfeely.com/clippy/)  
  *Utility:* Custom geometric shapes for royal arches, traditional Jharokha window frames, and crest shields.
- **Uiverse (Community UI Elements):**  
  *URL:* [uiverse.io](https://uiverse.io/)  
  *Utility:* Modern CSS buttons, glowing border cards, switch toggles, and loaders.

---

## 7. 🎯 Best Practices for Anshita Haute Couture Performance

1. **Strictly GPU-Accelerated**: Only animate `transform` (`translate3d`, `scale`) and `opacity` in scroll loops and continuous keyframes. Never animate `width`, `height`, `margin`, or `top` to prevent layout re-flows.
2. **Accessible Reduced-Motion**: Always preserve the `@media (prefers-reduced-motion: reduce)` block in `animations.css` to respect user device preferences.
3. **Session Guards**: Ensure heavyweight entrance curtains and preloaders fire only once per user session using `sessionStorage.getItem('anshita_preloader_seen')`.
4. **Mobile Optimization**: On touch viewports (<768px), throttle WebGL particle counts and disable heavy cursor trails to preserve 60fps scrolling and battery life.
