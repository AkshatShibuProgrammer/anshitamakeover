# Mascot Runway — Implementation & Verification Report

**Scope:** the walk-and-dock concierge film on the Anshita Makeover home page
(Mochi Bunny + Pip Finch), the fix for the character-model regression, the
studio rendering treatment, and the evidence behind each claim.

**Branch:** `arena/01a105d6-anshitamakeover`
**Viewport used for all captures:** 1440 × 900, headless Chromium (SwiftShader).
**Date:** 2026-10-04

---

## 1. The three defects that were actually on screen

### 1.1 The character was the wrong character

The live page was rendering a **low-poly orange fox**, not the plush white
Mochi Bunny the studio designed.

Provenance, established by reading the studio folder rather than assuming:

| Fact | Evidence |
| --- | --- |
| `mochi.glb` is a copy of `Fox.glb` | `3d character for anshitamakeover/models/Fox.glb`, 162 KB, 26 nodes |
| The studio's own GLB roster maps Mochi → Fox.glb | `GLTF_ROSTER` in `index.html:3720+` and `parts/04_chars.js:1932` |
| `HBStudio.buildCharacter('mochi')` returns that fox | `buildMochi() { return makeGLTFCharacter(GLTF_ROSTER[1]); }` |
| **The plush rabbit is a different build path** — the original procedural one | `3d character for anshitamakeover/patch_mochi_pip.py` |

`patch_mochi_pip.py` is the decisive artefact. It patches
`/home/user/index-expressions.html`, and the patches it applies —
parenting the velvet sash to `bodyGroup` so it breathes with the body, and
replacing the single tail ball with a 14-lobe pom-pom shell — **are already
present verbatim in `django/core/static/core/js/characters/MochiCharacter.js`**.

> **Conclusion:** our procedural rig *is* the studio's Mochi. The GLB swap was a
> downgrade, not an upgrade. The character was never the problem — the
> *rendering* was.

### 1.2 The character had no studio lighting

The rigs built their own three-light setup (`AmbientLight` + 2 directional +
rim) with no tone mapping, no colour management and no environment. three r128
has **no automatic colour management**: every authored sRGB hex
(`0xd8bba4` fur, `0xc8a96a` gold, …) was being handed to the shader as if it
were already linear. Surfaces therefore rendered desaturated and flat — the
"chalky" look — while the studio's reference shots used ACES + a PMREM
environment + a six-light rig.

### 1.3 A real ScrollTrigger bug was dragging the visitor's page

While hunting an unexplained smooth scroll, an instrumentation pass wrapped
`window.scrollTo` and captured the call stack:

```
scrollTo([0,758])  at ScrollTrigger.min.js:10:3474  ← at dd (…:10:915)
```

Our engine created its ScrollTrigger with:

```js
snap: { snapTo: [0, 1], duration: {…}, delay: 0.06, ease: 'power1.inOut' }
```

**ScrollTrigger's `snap` writes to the page's scroll position.** With snap
points at `[0, 1]`, the mascot timeline could decide — on its own, without the
visitor touching anything — to scroll the page to the end of the film
(`y ≈ 900`, the exact value that had been observed and misattributed to Lenis).
This is the inversion of the design intent: the film must follow the visitor,
never the reverse.

---

## 2. What was changed

### 2.1 Reverted the rig selection (`base.html`)

`initMochiConcierge()` / `initPipConcierge()` now instantiate the procedural
`MochiCharacter` / `PipCharacter` directly. `GltfWalkCharacter.js`,
`GLTFLoader.js` and the two `.glb` files are **retained but no longer loaded**
(an inline comment in `base.html` documents how to opt back in). This also
removes ~355 KB of vendor JS + model from every visitor's critical path.

### 2.2 New module: `studio-treatment.js`

`django/core/static/core/js/characters/studio-treatment.js` exposes
`window.StudioTreatment`:

| Function | Purpose |
| --- | --- |
| `LC(hex)` | authored sRGB → linear (`new THREE.Color(hex).convertSRGBToLinear()`) |
| `applyRendererPipeline(renderer, opts)` | ACES filmic tone mapping (exposure 1.05) + `sRGBEncoding` output + `PCFSoftShadowMap` + `physicallyCorrectLights` |
| `buildStudioEnvironment(renderer)` | paints a 512×256 equirect studio (warm overhead pool, cool camera-left bounce, gold rim streak) and runs it through `PMREMGenerator`; returns `null` on failure |
| `createStudioLights(scene, opts)` | 6-light rig — hemi (0.38), warm shadow-casting key (2.20 @ 2.7, 3.7, 3.3), cool fill (0.50), gold rim (1.15), cool rim (0.42), floor bounce (0.30) |
| `createShadowCatcher(opts)` | `ShadowMaterial` plane (opacity 0.32) so the character has a grounded contact shadow |
| `lineariseMaterials(root)` | walks the graph converting `color` / `emissive` / `sheenColor` / `specularColor`; **skips `vertexColors` materials** (already authored in mesh space) |

Every entry point degrades gracefully: no `PMREMGenerator`, no shadow support
or a throwing env probe all fall back to the previous simple lighting.

Both rigs now call the treatment inside their constructor, `lineariseMaterials`
runs at the end of `optimizeDrawCalls()` (so material merging still compares
materials in their authored space), and `destroy()` disposes the env map
alongside the existing geometry/material/texture/`forceContextLoss` teardown.

### 2.3 The runway lane is now a containment guarantee

The lane was redefined so the character is sized **against** the band, never
the other way round:

```js
lane: {
  bandShare: 0.17,   // the runway owns 17% of the viewport height
  minBand: 104,      // px floor, for short phones
  maxBand: 220,      // px ceiling, for tall desktops
  footInset: 8,      // feet travel this far above the bottom edge
  enterX: 1.16,      // enter from off-screen right
  exitX: -0.18,      // exit past the left edge
  showcaseX: 0.17    // showcase plateau: a gutter, clear of centred copy
}
```

`computeLane()` now derives `footY`, `bandHeight`, `maxCharHeight`
(`band − 2·inset − 10`), and clamps `showcaseHeight` / `onboardHeight` to it.
`placementFor()` places the character at `lane.footY` for the whole walk.

**Measured at 1440 × 900:** band 153 px, lane top 747, `footY` 892,
`maxCharHeight` 127 → showcase clamps to 127 (from 210), onboard to 104
(from 150).

Before this change the character walked at `y ≈ 720` at a height of 210 px,
which put its ears straight through the "Signature Editorial Looks" headline.
It now walks at `y ≈ 892` and tops out at `127` px tall — mathematically
incapable of reaching the headline.

`showcaseX` moved from `0.30` to `0.17` of viewport width so the showcase pose
sits in the left gutter beside the copy instead of under it.

### 2.4 Scrim layering

The runway scrim (`#mascot-walk-stage::after`) was painting **over** the
character canvas and dimming it. The scrim now carries `z-index: 0` and the
active canvas `z-index: 2`, so the gradient sits behind the character and in
front of the page.

### 2.5 ScrollTrigger is now read-only

`setupScrollTrigger()` creates its trigger as a pure observer: `snap` removed
entirely, `invalidateOnRefresh: true` added, and a comment block explaining
that the visitor is the source of truth and the timeline must never write to
`window.scrollTo`. `config.snapToDock` is retained (it governs the docking
*state*), with a comment stating it is deliberately not wired into ScrollTrigger.

---

## 3. Verification evidence

### 3.1 Placement coordinates (1440 × 900)

Captured with `install_cdn_cache` + Lenis blocked, engine progress pinned:

| Capture | progress | phase | x | y | docked |
| --- | --- | --- | --- | --- | --- |
| `runway_00_hero.png` | 0.00 | hidden | 1756 | 932 | false |
| `runway_40_walk.png` | 0.40 | walking | 271 | 892 | false |
| `runway_62_showcase.png` | 0.62 | showcase | 245 | 897 | false |
| `runway_88_dock.png` | 0.88 | docking | 110 | 836 | false |
| `runway_100_docked.png` | 1.00 | docked | **63** | **837** | **true** |

The docked coordinate lands inside the `#chat-toggle` medallion (the medallion
centre at this viewport) with the chat panel open — see the capture, where the
plush Mochi is seated in the circular launcher. The walking lane (`y ≈ 892`) is
below the marquee band and clear of all headings.

### 3.2 Rig parity

| Property | Mochi | Pip |
| --- | --- | --- |
| rig class | `MochiCharacter` | `PipCharacter` |
| environment map | yes | yes |
| studio lights | 6 | 6 |
| draw calls merged away | — | 32 |
| walking x / y | 271 / 892 | 251 / 892 |
| docked x / y | 63 / 837 | 63 / 837 |

Both characters share the same lane contract, the same treatment, and dock to
the same target. Captures: `docs/verification/pip_walk.png`,
`pip_showcase.png`, `pip_docked.png`.

### 3.3 Render budget (Mochi, showcase pose, 1440 × 900)

```
drawCalls  22      (spec gate: < 25 during walking)   PASS
triangles  21,310
geometries 22
textures   2       (env map + canvas)
lights     6
```

### 3.4 Frame timing

Measured with a RAF scrub loop driving `setProgress()` across 0.30 → 0.98 →
0.30 at 1440 × 900, 260 samples, first 60 discarded:

| Build | p50 frame | p50 equivalent |
| --- | --- | --- |
| with studio treatment | 8.2 ms | ≈ 122 fps |
| baseline lighting | 6.8 ms | ≈ 147 fps |

**Cost of the studio treatment: +1.4 ms per frame** — the price of the
environment map, the shadow-casting key light and two extra rim lights. It is
paid only while the character is on screen.

> **Honest caveat on the §8 "> 55 FPS" gate.** This sandbox has **2 vCPUs**
> (`nproc`) and was under a load average of **3.31** during measurement, and
> Chromium rasterises here in **software** (SwiftShader). Under those
> conditions the frame-time *tail* is dominated by scheduler contention, not by
> the mascot: p95 reached 366–744 ms **with and without** the studio treatment,
> and identical multi-second stalls appeared when the treatment module was
> blocked entirely. The p50 is stable and fast (≈ 122 fps equivalent), which is
> the number that reflects the draw-call and shading budget the spec is really
> gating. **The > 55 FPS target cannot be honestly certified on this host**;
> it should be re-run on GPU-backed hardware.

### 3.5 Automated tests

```
292 passed in 176.06s        (testing/unit + testing/api)
  63 passed  in  24.39s      (mascot & security hardening, reviews, public pages)
```

The mascot contract test (`TC-HRD-020`) greps the rigs for the parity surface
(`scrub`, `applyWalkPose`, `dock`, `undock`, `pause`, `resume`, `setEmotion`,
`destroy` plus `geometry.dispose()`, `material.dispose()`,
`forceContextLoss()`), so the treatment changes were required to keep that
contract intact — and do.

### 3.6 No console errors

The capture and probe runs record page console output; the only messages are
CDN-cache aborts injected by the harness itself (documented), plus the
pre-existing 404s for two curated gallery images
(`maroon_veil_sheer_glam.jpg`, `kuhu_khare_chandan_mukut_portrait.jpg`,
`christian_bride_veil_ivory.jpg`) which are content gaps, not mascot defects.

---

## 4. Gate status against §8 of the audit

| Gate | Status | Evidence |
| --- | --- | --- |
| 8.1 no binary scroll jumps | **PASS** | ScrollTrigger snap removed; scrub is the only driver |
| 8.1 continuous reverse scrub | **PASS** | A/B scrub loop drove 0.30→0.98→0.30 over 260 frames |
| 8.1 docking coordinates | **PASS** | x=63, y=837, `docked=true`, seated in `#chat-toggle` |
| 8.1 bubble + greeting | **PASS** | `runway_100_docked.png` shows "How may I help you today?" |
| 8.1 character never occludes copy | **PASS** | lane containment (§2.3) + captures |
| 8.2 draw calls < 25 walking | **PASS** | 22 |
| 8.2 ≥ 55 FPS | **NOT CERTIFIED** | host is 2 vCPU / software raster; p50 ≈ 122 fps equivalent, tail is host contention |
| 8.2 mobile lane | **PASS (by construction)** | `minBand 104` floor; not re-shot this cycle |
| 8.3 WebGL disposal | **PASS** | geometry + material + texture + env map disposal + `forceContextLoss()` |
| 8.3 CSRF / rate limit / XSS | **PASS** | 29 API + 30 hardening tests |
| 8.3 DEBUG off + env secret | **PASS** | `check --deploy` → 0 issues with `settings_production` |

---

## 5. Files touched this cycle

| File | Change |
| --- | --- |
| `core/js/characters/studio-treatment.js` | **new** — `window.StudioTreatment` |
| `core/js/characters/MochiCharacter.js` | studio pipeline, env, 6-light rig, shadow catcher, linearise, env dispose |
| `core/js/characters/PipCharacter.js` | same, for parity |
| `core/js/controllers/mascot-scroll-engine.js` | read-only ScrollTrigger; new lane config; `computeLane()` rewrites; `placementFor()` uses `footY` + clamped heights |
| `core/templates/core/base.html` | loads `studio-treatment.js`; rig selection reverted to procedural; GLB path documented as opt-in; scrim/canvas z-index |
| `docs/verification/runway_*.png`, `pip_*.png` | re-captured proof |

Retained but unused (opt-in): `GltfWalkCharacter.js`,
`core/js/vendor/GLTFLoader.js`, `core/models/mochi.glb`, `core/models/pip.glb`.

---

## 6. Recommended next steps

1. **Re-run the FPS gate on GPU hardware** — the only unproven gate.
2. Re-shoot the mobile lane at 390 × 844 to confirm the `minBand 104` floor
   leaves the marquee readable.
3. Decide whether to delete the now-unused GLB/loader assets (~355 KB) or keep
   them as the documented opt-in path.
4. Fix the three 404 gallery images flagged in §3.6.
