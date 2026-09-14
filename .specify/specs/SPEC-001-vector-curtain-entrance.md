# Feature Specification: Haute Couture Vector Entrance & Dual-Curtain System

**Feature Branch:** `feature/vector-curtain-entrance`  
**Spec ID:** `SPEC-001`  
**Governing Document:** [constitution.md](file:///.specify/memory/constitution.md)  
**Status:** Approved for Planning

---

## 1. Executive Summary & Problem Description
The platform currently utilizes a raster MP4 preloader (`Logo_reveal_animation_beauty_brand_delpmaspu_.mp4`). This causes browser media decoder initialization delay (100–300ms), 24fps stutter on modern 60/120Hz displays, visible letterbox boundaries against the dark theme, and an unnatural opacity fade that fails to emulate the architectural luxury feel of benchmark sites like [evagher.com](https://evagher.com/en).

This specification defines the replacement of the raster video preloader with:
1. An SVG vector monogram path engine with animated stroke drawing.
2. A dual-curtain horizontal split door mechanism (`.curtain-left` & `.curtain-right`).
3. Synchronized WebGL background handoff and instant skip accessibility.

---

## 2. User Stories & Persona Acceptance

### User Story 1: First-Time Luxury Bridal Client
> *As a prospective bride visiting the website for the first time,*  
> *I want to see an immediate, fluid, golden brand crest drawing itself seamlessly on deep velvet black,*  
> *So that I instantly perceive the brand as high-end, bespoke, and equivalent to global luxury couture houses.*

### User Story 2: Returning Client / Frequent Navigator
> *As a client navigating back and forth between "Home", "Bridal Services", and "Gallery",*  
> *I do NOT want to be forced to re-watch any preloader animation,*  
> *So that page navigation is instant, fluid, and frictionless.*

### User Story 3: Performance & Accessibility Conscious Visitor
> *As a visitor on a mobile phone or with keyboard navigation,*  
> *I want the option to press the Escape key or tap "Skip Intro" to instantly enter the site,*  
> *So that I have complete control over my browsing experience.*

---

## 3. Functional Requirements

| Req ID | Requirement Description | Success Metric |
| :--- | :--- | :--- |
| **FR-01** | Replace HTML `<video>` preloader with inline mathematical `<svg>` crest | 0 video decoders instantiated on initial load; payload < 15KB |
| **FR-02** | Stroke-dashoffset drawing animation across monogram curves | Smooth 60–120 FPS draw completion in 1.6s |
| **FR-03** | Dual curtain horizontal parting (`.curtain-left` / `.curtain-right`) | Split down exact vertical 50% line; opens with `cubic-bezier(0.77, 0, 0.175, 1)` |
| **FR-04** | Session persistence guard | Subsequent loads skip preloader instantly without FOUC |
| **FR-05** | Keyboard / Click bypass controls | `Escape` key or click anywhere opens curtains instantly |
| **FR-06** | Synchronized WebGL shader burst | Three.js ripple intensity scales up as curtains part |

---

## 4. Non-Functional Requirements
- **Performance:** Preloader DOM must render at frame 0 (Time to First Frame < 50ms on 4G).
- **Smoothness:** Zero jank or layout reflows during curtain parting (`will-change: transform`).
- **Browser Compatibility:** Flawless execution across Chrome, Safari iOS, Edge, and Firefox.
- **Accessibility:** Respects `prefers-reduced-motion` by bypassing the intro animation automatically.
