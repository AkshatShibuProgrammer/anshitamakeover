# Feature Specification: Pip Flight Kinematics, Draggable Relocation & Editorial Refinement

**Feature Branch:** `arena/01a105d6-anshitamakeover`  
**Spec ID:** `SPEC-020`  
**Governing Documents:** `.specify/memory/constitution.md`, `.specify/memory/constitution-pip-mascot-concierge.md`  
**Status:** In Progress  
**Estimated Complexity:** High (Three.js Flight Curves, Pointer Drag-and-Drop Physics, Radiating Landing Pulse, DOM Pinned One-Time Transformation, Luxury Copy Re-alignment)

---

## 1. Executive Summary & Problem Description

### 1.1 Problems Addressed
1. **Pip Entrance & Movement Fidelity**:
   - Rather than an abrupt vertical rise, the user requested an organic, magical flight animation: Pip flies in from the edge of the viewport with rapid wing flaps, circles in 3D space, and settles gently into the dock, accompanied by an expanding radiant circular wave/halo.
   - When a user clicks and drags Pip across the viewport, Pip must take flight, actively flap wings, follow the pointer across the screen, and glide down to settle at the new user-chosen dock location with the settling ring effect.
2. **Unprofessional Ticker Marquees**:
   - The double marquee crawling text (`✦ BRIDAL COUTURE ✦ AIRBRUSH ARTISTRY...` and `◈ RAJASTHANI LEHENGA DRAPE ◈ SOUTH INDIAN SILK BRIDE...`) looks noisy, cheap, and like an automated template rather than a bespoke luxury bridal studio.
3. **Exaggerated & Unrealistic Copywriting**:
   - Terms like *"HAUTE COUTURE METHOLEGY / The 4 Sacred Rituals of Bridal Grace / Skin Metallurgy / Sacred Geometry"* sound exaggerated, pseudo-scientific, and artificial. No high-end Indian bridal artist speaks this way. It must be replaced with grounded, elegant, authentic bridal terminology (Dermal Prep, Banarasi & Dupatta Draping, HD Airbrush Longevity, Mandap Radiance).
4. **Heavy Clunky Scroll Scrubber vs Clean Fixed Showcase**:
   - Replace the heavy 48-frame canvas scrubber with a pinned, one-time split view:
     - Left: Real bridal photo transformation.
     - Right: Transparent service pricing and character animation.
     - Pinned scroll: Locks screen gracefully for one scroll gesture to reveal transformation & pricing, then permanently unlocks to natural scroll so visitors never get stuck in scroll hijacking.

---

## 2. User Stories & Acceptance Criteria

### User Story 1: Organic Flight & Relocatable Mascot (Pip)
*As a visitor, I want Pip to fly in gracefully, land with a radiant gold wave, and let me drag Pip anywhere on the screen so it flies to my preferred position without obstructing content.*
- **AC 1.1**: On entrance ($t=2.5\text{s}$), Pip flies along an arced 3D Bezier curve with high-frequency wing beats (`this.flap = 2.4`), descends, and settles at $y=0$ at $t=3.8\text{s}$.
- **AC 1.2**: Upon settling, an animated radiating circle (`.cc-landing-ring`) expands outward with gold metallic dissipation.
- **AC 1.3**: The user can drag Pip anywhere on the screen. On drag start, Pip enters flight posture with active wing flapping and tilting into the movement vector.
- **AC 1.4**: On drop, Pip glides down to the new screen coordinates, returns to idle posture, and triggers the radiating landing ring.

### User Story 2: Clean Luxury Editorial Whitespace (No Marquees)
*As a prospective bride, I want a calm, elegant editorial experience without cheap crawling text banners.*
- **AC 2.1**: The double crawling ticker marquee section (`.marquee-band`) is completely removed from the DOM and CSS.
- **AC 2.2**: Generous luxury whitespace and subtle gold hair-line dividers separate the Hero and Signature Looks sections.

### User Story 3: Pinned One-Time Transformation & Before/After Showcase
*As a visitor exploring bridal services, I want to see genuine before-and-after transformations and transparent pricing without frustrating scroll traps.*
- **AC 3.1**: The section features a 50/50 split: Left side displays high-resolution authentic bridal transformation (Before: skin prep/dermal base; After: full mandap radiance); Right side displays transparent discipline pricing and character reaction.
- **AC 3.2**: When scrolling into the section, the viewport locks briefly for one smooth scrub transition revealing the transformation and pricing tiers.
- **AC 3.3**: Once revealed (or if scrolled past once), the lock disengages permanently for that session (`sessionStorage.setItem('trans_revealed', '1')`), allowing uninterrupted natural scrolling.

### User Story 4: Grounded, Authentic Indian Bridal Copy & Experience Truths (#confirmed)
*As a discerning bride, I want truthful metrics, grounded luxury terminology, and complete ecosystem tie-ups.*
- **AC 4.1 (#confirmed)**: Anshita Sinha has **3 years of professional experience** (not 12+ years, not 1200+ brides). Metric counter displays: `3+ Years of Artistry`, `100+ Brides Celebrated`.
- **AC 4.2 (#confirmed)**: Eliminate pseudo-scientific "4 Pillars of Luxury Bridal Artistry" and "Skin Metallurgy". Replace with genuine Before/After transformations and clean service offerings.
- **AC 4.3 (#confirmed)**: Categorize cultural makeup with authentic photos: Bengali Bride (Mukut & Chandan), Christian Bride (Cathedral Veil), Sangeet Glamour, Royal Vivah Bridal. Present non-makeup styling (Saree draping, Hair styling, Nail art) in clean auxiliary lists *without* photo clutter.
- **AC 4.4 (#confirmed)**: Partner ecosystem tie-ups:
  - Photography & Cinematography: Starting from ₹80,000.
  - Full Event Management, Decorators & Facilitators: Enquire for combination discount (no starting price).
  - Royal Catering & Banqueting: Strategic partner tie-up.
- **AC 4.5 (#confirmed)**: Cinematic Repertoire (Works Wheel) pauses page scroll on first arrival, smoothly animates the downward/rotational movement of 3D cards, and permanently frees scroll. All cards show real 4K photos.
- **AC 4.6 (#confirmed)**: Remove the noisy city rotator from immediate hero curtain-parting view. Move regional cities to an elegant, quiet regional coverage strip at the bottom of the page (Jabalpur Flagship Studio, Damoh, Katni, Bhopal, Indore, Lucknow, Jhansi, All Over India).
- **AC 4.7 (#confirmed)**: Google Maps & website footer clearly states: "Flagship Studio in Jabalpur with Destination Wedding Services Available All Over India".

---

## 3. Verification & Acceptance Gate
- [ ] Pip performs 3D flight entrance on load and lands with gold circular halo wave.
- [ ] Pip is draggable to any screen position, flying dynamically while dragged and landing with ring pulse.
- [ ] Metric counters reflect 3+ years experience and 100+ brides.
- [ ] Artificial "4 Pillars" section removed in favor of authentic Before/After transformation.
- [ ] Cinematic Repertoire (Works Wheel) executes one-time downward motion pause and frees scroll.
- [ ] Dedicated cultural makeup sections show real photos (Bengali, Christian, Sangeet, Bridal); non-makeup services (saree, hair, nails) listed without photo clutter.
- [ ] Wedding partner tie-ups clearly featured: Photography starting from ₹80,000; Event management/decor "Enquire for combination discount"; Caterer tie-up.
- [ ] Regional coverage strip placed at page bottom with Damoh, Katni, Jabalpur Flagship, and All Over India.
- [ ] Strict `#confirmed` guardrail enforced for all future AI agents.
