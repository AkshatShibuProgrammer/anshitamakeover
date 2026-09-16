# SpecKit: Module 1: Sinha Standalone Asset Archival

**Phase:** Phase 1: Sinha Group Webpage Archival  
**Module Directory:** `mod_01_sinha_assets_archive`  
**Status:** In Specification  

---

## 1. Module Overview & Objective
Archive standalone HTML/SVG assets, font bundles, and preview renders under resources/sinha_group/ without affecting runtime Django templates.

---

## 2. Granular Functional Requirements
- **FR-P1-01**:  Create resources/sinha_group/ directory hierarchy
- **FR-P1-02**:  Save standalone HTML visualizer with all embedded SVGs
- **FR-P1-03**:  Archive vector assets (sinha_royal_c2_crest.svg, zxixi_cleaned.svg)
- **FR-P1-04**:  Document usage instructions in resources/sinha_group/README.md

---

## 3. Architecture & Key Files Impacted
- Implementation scripts and templates will reside inside or be referenced by this module.
- Validation checks and unit tests will log results directly to this folder.

---

## 4. Verification Checklist
- [x] Requirements implemented without breaking existing views
- [x] Automated syntax and Django check passed
- [x] UI and responsiveness verified on mobile and desktop
