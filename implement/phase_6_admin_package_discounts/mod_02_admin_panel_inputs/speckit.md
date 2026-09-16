# SpecKit: Module 2: Admin Panel & AI Co-Pilot Controls

**Phase:** Phase 6: Admin Package Floor Prices & Max Discounts  
**Module Directory:** `mod_02_admin_panel_inputs`  
**Status:** In Specification  

---

## 1. Module Overview & Objective
Expose the new floor price and discount fields in Django Admin and the live Quick Admin overlay.

---

## 2. Granular Functional Requirements
- **FR-P6-04**:  Update core/admin.py to show min_negotiated_price and max_discount_percent
- **FR-P6-05**:  Add price floor and discount inputs into Quick Admin panel modal
- **FR-P6-06**:  Connect Admin AI Co-Pilot command parser to allow voice/text commands for package floors

---

## 3. Architecture & Key Files Impacted
- Implementation scripts and templates will reside inside or be referenced by this module.
- Validation checks and unit tests will log results directly to this folder.

---

## 4. Verification Checklist
- [x] Requirements implemented without breaking existing views
- [x] Automated syntax and Django check passed
- [x] UI and responsiveness verified on mobile and desktop
