# SPEC.md — Premium Three.js Ateliers & Always-Free Oracle Cloud Architecture

## 1. Executive Summary & Brand Positioning
- **Atelier**: Anshita Makeover (Haute Couture Bridal Atelier).
- **Authentic Credentials**: 3+ Years of Dedicated Artistry · 100+ Happy Brides Transformed.
- **Formulation Reality**: Pro Long-Wear Luxury (Huda Beauty, NARS, Kryolan Derma, PAC, Cry-proof Airbrushing) — grounded, authentic, prestigious.
- **Experience Philosophy**: Editorial elegance inspired by Vogue & Sabyasachi, powered by Three.js WebGL physics, zero cartoonish gimmicks.
- **Infrastructure Target**: 100% Free Forever on Oracle Cloud Always Free Tier (ARM 4 OCPU, 24GB RAM) with 100% media offloaded to Meta (Instagram/Facebook) and edge CDN so server bandwidth consumption is virtually zero.

---

## 2. Infrastructure & Zero-Cost Architecture (Oracle Cloud Free Tier)

### 2.1 The "Always Free" Constraint & Meta Media Strategy
Oracle Cloud provides:
- 4 OCPU ARM Ampere compute cores.
- 24 GB RAM.
- 200 GB storage.
- 10 TB/month outbound bandwidth.

To guarantee the site stays **100% free forever without hitting limits**:
1. **Video & Heavy Media Offloading**:
   - All bridal reels and cinema videos stream directly from **Instagram / Facebook CDN edge nodes** (`scontent.cdninstagram.com` via reel shortcodes & iframe/video embeds).
   - The Oracle server NEVER serves raw 50MB-100MB MP4 files to users. Bandwidth on Oracle = **0 KB for video streams**.
2. **Free Cloudflare Proxy / Edge CDN**:
   - Put Cloudflare (Free Tier) in front of the Oracle VM for SSL, DDoS mitigation, and global edge caching of HTML/CSS/JS.
   - Result: 95%+ of static requests are absorbed at Cloudflare edge, keeping Oracle CPU idle (< 5%).
3. **Optimized SQLite / PostgreSQL**:
   - Lightweight Django app running Gunicorn + WhiteNoise + UFW firewall.

---

## 3. Frontend & Three.js Architecture

### 3.1 Website-Wide Three.js WebGL Atmosphere
- **Hero & Ambient Stages**: GPU-accelerated gold stardust / floating mica particle field with cursor gravitational pull (`Three.Points` with custom GLSL shader or additive blending).
- **Haute Couture Depth & Parallax**: Three.js raycasting depth tilt on signature looks without heavy DOM thrashing.
- **Performance Constraints**: Capped at 60fps, throttled on mobile/battery saver, `powerPreference: "high-performance"`, proper disposal on page unload to prevent WebGL memory leaks.

### 3.2 Real 3D Anshita Character Engine
- **Model Standard**: Rigged 3D GLB/GLTF humanoid model wearing traditional couture lehenga & jewelry.
- **Physics Bones**: Secondary spring physics on hair strands, jhumkas, and dupatta borders using Verlet integration / Three.js damping.
- **Cursor Tracking & Inverse Kinematics**:
  - Head (`Head` bone) and neck (`Neck` bone) quaternion SLERP following normalized mouse coordinates $(x, y)$.
  - Natural micro-movements (subtle breathing cycle on chest bone, periodic blink cycle).
- **Facial Blendshapes (Morph Targets)**:
  - `eyeBlinkLeft`, `eyeBlinkRight`
  - `mouthSmile` (warm welcome)
  - `browInnerUp` (attentive listening)
  - `jawOpen` / `viseme_aa` (speech delivery)
- **Interactive Concierge Integration**:
  - When user selects a bridal question, the character transitions expressions (`idle` -> `listening` -> `explaining` -> `delighted`).

---

## 4. Free Tools Required & Ecosystem

1. **Oracle Cloud Free Tier Account** (Always Free Compute + VCN + Public IP) — Free.
2. **Cloudflare Free Plan** (DNS + Edge Caching + Free SSL) — Free.
3. **Blender 4.x** (3D mesh sculpting, bone weight painting, export to `.glb` with Draco compression) — Free & Open Source.
4. **Ready Player Me / MakeHuman** (Base rigged female mesh with blendshape topology) — Free.
5. **Three.js + GLTFLoader + DRACOLoader** (In-browser rendering) — Built into project.
6. **GSAP + ScrollTrigger + Lenis** (Smooth scroll & timeline sequencing) — Built into project.
