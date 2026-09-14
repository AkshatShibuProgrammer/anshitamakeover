# Stage 3: WebGL Background Handoff & Micro-Interactions

## 1. Context & Problem Statement
Currently, Three.js runs quietly in the background on `#bg-canvas`, but there is no synchronized choreography between the preloader curtain parting and the 3D scene elements:
- The Three.js fluid ripples and ambient gold particles are rendered at a constant uniform rate, independent of user entry.
- On [evagher.com](https://evagher.com/en), the entrance triggers dynamic shader bursts, smooth scroll activation, and cursor physics that reward the user instantly.

---

## 2. Current State vs. Target State

```
CURRENT STATE:
[ Video Fade ] ──> [ Static Three.js Shader already running in background ]

TARGET STATE:
[ Curtain Parting ] ──> [ WebGL Shader Bloom Burst ] ──> [ Hero Typography Staggered Reveal ] ──> [ Interactive Fluid Ripple ]
```

| Metric / Attribute | Current State | Target State |
| :--- | :--- | :--- |
| **Shader Synchronization**| Decoupled; shader runs continuously | Uniform parameter `u_entranceProgress` linked to curtain parting |
| **Particle Dynamics** | Static ambient drift | Burst particle expansion on curtain reveal, settling into gentle drift |
| **Typography Reveal** | Appears statically as opacity clears | Split-text staggered upward reveal (`transform: translateY(40px)` -> `0`) |
| **Interactivity** | Mouse only affects basic uniform position | Interactive mouse velocity trail with fluid distortion |
| **Bypass / Skip Controls**| No skip option; user forced to wait | "Skip Intro" micro-button + `Escape` key + Click anywhere to instantly bypass |

---

## 3. Technical Implementation Specification

### 3.1 WebGL Shader Uniform Integration
In `core/static/core/js/main.js` (or Three.js init script):
```glsl
// In vertex / fragment shader
uniform float u_time;
uniform float u_entrance; // 0.0 before curtain opens, smoothly interpolates to 1.0
uniform vec2 u_mouse;

void main() {
    // Expand wave amplitude and gold luminescence as entrance progresses
    float wave = sin(vUv.x * 10.0 + u_time * 0.8) * cos(vUv.y * 10.0 + u_time * 0.8) * u_entrance;
    vec3 color = mix(vec3(0.04, 0.035, 0.03), vec3(0.83, 0.68, 0.21), wave * 0.4);
    gl_FragColor = vec4(color, 1.0);
}
```

### 3.2 Hero Staggered Typography Animation
When `.is-revealed` is added to the preloader:
```css
.hero-content .reveal-text {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 1s cubic-bezier(0.16, 1, 0.3, 1), transform 1s cubic-bezier(0.16, 1, 0.3, 1);
}

body.site-loaded .hero-content .reveal-text:nth-child(1) {
    transition-delay: 0.3s;
    opacity: 1;
    transform: translateY(0);
}

body.site-loaded .hero-content .reveal-text:nth-child(2) {
    transition-delay: 0.5s;
    opacity: 1;
    transform: translateY(0);
}

body.site-loaded .hero-content .reveal-text:nth-child(3) {
    transition-delay: 0.7s;
    opacity: 1;
    transform: translateY(0);
}
```

### 3.3 Micro-Interaction: Skip & Keyboard Accessibility
```javascript
// Quick bypass mechanism
function skipPreloader() {
    const preloader = document.getElementById('preloader');
    if (!preloader || preloader.classList.contains('is-revealed')) return;
    
    preloader.classList.add('is-revealed');
    document.body.classList.add('site-loaded');
    sessionStorage.setItem('anshita_preloader_seen', 'true');
    
    setTimeout(() => {
        preloader.style.display = 'none';
    }, 1200);
}

// Bind to Escape key and skip button
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') skipPreloader();
});
```

---

## 4. Acceptance Criteria
1. **Fluid Burst**: Visually perceptible blossoming of gold ambient light when the curtains part.
2. **Instant Skip**: Pressing `ESC` or clicking "Skip Intro" instantly opens curtains without jitter.
3. **Typography Stagger**: Hero title glides up in a coordinated sequence, matching luxury editorial standards.
