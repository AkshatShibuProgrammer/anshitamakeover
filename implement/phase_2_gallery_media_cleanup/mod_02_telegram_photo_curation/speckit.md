# SpecKit: Module 2: Telegram High-Res Photos Curation

**Phase:** Phase 2: Gallery & Media Cleanup  
**Module Directory:** `mod_02_telegram_photo_curation`  
**Status:** In Specification  

---

## 1. Module Overview & Objective
Identify authentic real photos from Telegram Desktop (e.g. WA0316, WA0317, WA0334, WA0349), optimize to web quality, and store in structured folders.

---

## 2. Granular Functional Requirements
- **FR-P2-04**:  Filter and copy authentic 3024x4032 photos to core/static/core/images/authentic/
- **FR-P2-05**:  Compress WebP/JPEG thumbnails for fast mobile loading
- **FR-P2-06**:  Create photo registry index

---

## 3. Architecture & Key Files Impacted
- Implementation scripts and templates will reside inside or be referenced by this module.
- Validation checks and unit tests will log results directly to this folder.

---

## 4. Verification Checklist
- [x] Requirements implemented without breaking existing views
- [x] Automated syntax and Django check passed
- [x] UI and responsiveness verified on mobile and desktop
