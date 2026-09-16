# SpecKit: Module 1: Django Package Model Schema Extension

**Phase:** Phase 6: Admin Package Floor Prices & Max Discounts  
**Module Directory:** `mod_01_package_model_schema`  
**Status:** In Specification  

---

## 1. Module Overview & Objective
Add min_negotiated_price, max_discount_percent, and allow_ai_negotiation fields to MakeupPackage model.

---

## 2. Granular Functional Requirements
- **FR-P6-01**:  Update MakeupPackage model in core/models.py
- **FR-P6-02**:  Generate and apply Django database migrations
- **FR-P6-03**:  Set sensible defaults (e.g. min floor 80% of price, max discount 20%)

---

## 3. Architecture & Key Files Impacted
- Implementation scripts and templates will reside inside or be referenced by this module.
- Validation checks and unit tests will log results directly to this folder.

---

## 4. Verification Checklist
- [x] Requirements implemented without breaking existing views
- [x] Automated syntax and Django check passed
- [x] UI and responsiveness verified on mobile and desktop
