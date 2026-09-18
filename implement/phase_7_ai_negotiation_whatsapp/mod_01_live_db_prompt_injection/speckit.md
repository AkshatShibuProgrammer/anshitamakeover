# SpecKit: Module 1: Live Database Context & Guardrails

**Phase:** Phase 7: Dynamic AI Negotiation & WhatsApp Privilege Cards  
**Module Directory:** `mod_01_live_db_prompt_injection`  
**Status:** In Specification  

---

## 1. Module Overview & Objective
Dynamically inject real-time package prices, min floors, and coupon rules from the database into Gemini prompt.

---

## 2. Granular Functional Requirements
- **FR-P7-01**:  Query active MakeupPackage records in gemini_chat()
- **FR-P7-02**:  Formulate dynamic system prompt with strict floor pricing guardrails
- **FR-P7-03**:  Enforce Rule

---

## 3. Architecture & Key Files Impacted
- Implementation scripts and templates will reside inside or be referenced by this module.
- Validation checks and unit tests will log results directly to this folder.

---

## 4. Verification Checklist
- [x] Requirements implemented without breaking existing views
- [x] Automated syntax and Django check passed
- [x] UI and responsiveness verified on mobile and desktop
