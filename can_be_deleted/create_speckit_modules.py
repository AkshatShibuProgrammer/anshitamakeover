import os
from pathlib import Path

base_impl = Path('implement')

# Define each phase, its modules, and the speckit file contents
phase_modules_config = {
    'phase_1_resources_archive': {
        'title': 'Phase 1: Sinha Group Webpage Archival',
        'modules': [
            ('mod_01_sinha_assets_archive', 'Module 1: Sinha Standalone Asset Archival',
             'Archive standalone HTML/SVG assets, font bundles, and preview renders under resources/sinha_group/ without affecting runtime Django templates.',
             ['FR-P1-01: Create resources/sinha_group/ directory hierarchy',
              'FR-P1-02: Save standalone HTML visualizer with all embedded SVGs',
              'FR-P1-03: Archive vector assets (sinha_royal_c2_crest.svg, zxixi_cleaned.svg)',
              'FR-P1-04: Document usage instructions in resources/sinha_group/README.md']),
            
            ('mod_02_django_studio_routing', 'Module 2: Django Studio Route Verification',
             'Maintain the active Django view for /sinha-logo-studio/ while referencing the resources directory for documentation.',
             ['FR-P1-05: Ensure core/urls.py retains /sinha-logo-studio/ route',
              'FR-P1-06: Add developer link in admin/footer pointing to studio route',
              'FR-P1-07: Verify 200 OK response on Django dev server'])
        ]
    },
    'phase_2_gallery_media_cleanup': {
        'title': 'Phase 2: Gallery & Media Cleanup',
        'modules': [
            ('mod_01_instagram_media_links', 'Module 1: Instagram Links Documentation',
             'Extract and compile all scraped and manual Instagram post/reel URLs, captions, and shortcodes into a clean text/notepad file.',
             ['FR-P2-01: Create resources/instagram_media_links.txt',
              'FR-P2-02: Format with Category, Shortcode, Direct Post URL, and Caption',
              'FR-P2-03: Include both photo lookbooks and video reels']),
            
            ('mod_02_telegram_photo_curation', 'Module 2: Telegram High-Res Photos Curation',
             'Identify authentic real photos from Telegram Desktop (e.g. WA0316, WA0317, WA0334, WA0349), optimize to web quality, and store in structured folders.',
             ['FR-P2-04: Filter and copy authentic 3024x4032 photos to core/static/core/images/authentic/',
              'FR-P2-05: Compress WebP/JPEG thumbnails for fast mobile loading',
              'FR-P2-06: Create photo registry index']),
            
            ('mod_03_person_lookbook_grouping', 'Module 3: Person/Look Grouping Engine',
             'Group multiple photos of the same person together (e.g. Bengali Bride - 4 looks) and add interactive "View All Looks" lookbook modals.',
             ['FR-P2-07: Add look_group or person_id field/attribute to gallery data',
              'FR-P2-08: Render primary cover photo on grid with badge "✦ 4 Looks of this Bride"',
              'FR-P2-09: Connect lookbook modal slider to cycle through the group photos']),
            
            ('mod_04_quarantine_obsolete_files', 'Module 4: Quarantining Obsolete Files',
             'Move discarded test scripts, temporary AI images, and outdated scratch files into can_be_deleted/ folder.',
             ['FR-P2-10: Create can_be_deleted/ directory',
              'FR-P2-11: Move scratch test scripts and unused images to can_be_deleted/',
              'FR-P2-12: Create manifest log of quarantined items'])
        ]
    },
    'phase_3_sinha_vector_footer': {
        'title': 'Phase 3: Sinha Vector Crest in Footer',
        'modules': [
            ('mod_01_footer_vector_crest', 'Module 1: Concept 02 Vector Crest Integration',
             'Embed the authentic Concept 02 pure vector crest (with ZXiXi01 elder contours) into the footer with 24K gold styling.',
             ['FR-P3-01: Create reusable template include core/templates/core/includes/sinha_c2_footer_crest.html',
              'FR-P3-02: Apply responsive 24K metallic gold styling and hover glow',
              'FR-P3-03: Position cleanly above admin link with "Designed & Endorsed by The Sinha Family Group"',
              'FR-P3-04: Verify mobile and desktop alignment'])
        ]
    },
    'phase_4_preloader_enhancement': {
        'title': 'Phase 4: Preloader Animation & Typography Scaling',
        'modules': [
            ('mod_01_stage_and_text_resizing', 'Module 1: Preloader Stage & Font Scaling',
             'Scale up the preloader monogram stage and brand typography for prominent luxury visibility.',
             ['FR-P4-01: Increase .crest-svg-container dimensions from 320px to min(440px, 88vw)',
              'FR-P4-02: Enlarge ANSHITA MAKEOVER typography font sizes and stroke weight',
              'FR-P4-03: Ensure stroke-dashoffset animation timing remains fluid at 60-120fps',
              'FR-P4-04: Test on mobile viewports (<480px) to prevent viewport clipping'])
        ]
    },
    'phase_5_mobile_mode_preview': {
        'title': 'Phase 5: Interactive Mobile Mode Viewport Simulator',
        'modules': [
            ('mod_01_mobile_frame_simulator', 'Module 1: Mobile Mode Simulator Component',
             'Implement a floating toolbar button allowing users/admins to toggle the entire website into a live mobile device frame directly on desktop.',
             ['FR-P5-01: Create mobile mode toggle button in menu / navigation bar',
              'FR-P5-02: Implement responsive iframe / container wrapper (390px x 844px iPhone canvas)',
              'FR-P5-03: Allow instant switching between Desktop Full View and Mobile Simulated View',
              'FR-P5-04: Persist preference in sessionStorage'])
        ]
    },
    'phase_6_admin_package_discounts': {
        'title': 'Phase 6: Admin Package Floor Prices & Max Discounts',
        'modules': [
            ('mod_01_package_model_schema', 'Module 1: Django Package Model Schema Extension',
             'Add min_negotiated_price, max_discount_percent, and allow_ai_negotiation fields to MakeupPackage model.',
             ['FR-P6-01: Update MakeupPackage model in core/models.py',
              'FR-P6-02: Generate and apply Django database migrations',
              'FR-P6-03: Set sensible defaults (e.g. min floor 80% of price, max discount 20%)']),
            
            ('mod_02_admin_panel_inputs', 'Module 2: Admin Panel & AI Co-Pilot Controls',
             'Expose the new floor price and discount fields in Django Admin and the live Quick Admin overlay.',
             ['FR-P6-04: Update core/admin.py to show min_negotiated_price and max_discount_percent',
              'FR-P6-05: Add price floor and discount inputs into Quick Admin panel modal',
              'FR-P6-06: Connect Admin AI Co-Pilot command parser to allow voice/text commands for package floors'])
        ]
    },
    'phase_7_ai_negotiation_whatsapp': {
        'title': 'Phase 7: Dynamic AI Negotiation & WhatsApp Privilege Cards',
        'modules': [
            ('mod_01_live_db_prompt_injection', 'Module 1: Live Database Context & Guardrails',
             'Dynamically inject real-time package prices, min floors, and coupon rules from the database into Gemini prompt.',
             ['FR-P7-01: Query active MakeupPackage records in gemini_chat()',
              'FR-P7-02: Formulate dynamic system prompt with strict floor pricing guardrails',
              'FR-P7-03: Enforce Rule: AI NEVER quotes below min_negotiated_price']),
            
            ('mod_02_negotiation_flow_logic', 'Module 2: Progressive Negotiation & Budget Inquiries',
             'Prompt AI to ask for wedding date, event location, and budget when user requests a discount.',
             ['FR-P7-04: Handle budget inquiry: ask for date, venue, and guest count',
              'FR-P7-05: If budget is within allowable range, offer best privilege rate above floor',
              'FR-P7-06: If budget is below floor, offer exact floor + free add-ons/alternatives']),
            
            ('mod_03_whatsapp_privilege_card', 'Module 3: Animated WhatsApp Privilege Chat Card',
             'Format the AI response with rich animated tables and a direct 1-click WhatsApp privilege booking button.',
             ['FR-P7-07: Generate unique VIP Privilege Token (e.g. VIP-CONCIERGE-24K)',
              'FR-P7-08: Render rich markdown table with category, standard rate, privilege rate, and savings',
              'FR-P7-09: Embed 1-click WhatsApp button with pre-filled VIP message in chat bubble'])
        ]
    }
}

count_modules = 0
for phase_dir, pdata in phase_modules_config.items():
    phase_path = base_impl / phase_dir
    phase_path.mkdir(parents=True, exist_ok=True)
    
    for mod_dir, mod_title, mod_desc, reqs in pdata['modules']:
        count_modules += 1
        mod_path = phase_path / mod_dir
        mod_path.mkdir(parents=True, exist_ok=True)
        
        speckit_file = mod_path / 'speckit.md'
        reqs_formatted = '\n'.join([f"- **{r.split(':')[0]}**: {r.split(':')[1]}" if ':' in r else f"- {r}" for r in reqs])
        
        content = f"""# SpecKit: {mod_title}

**Phase:** {pdata['title']}  
**Module Directory:** `{mod_dir}`  
**Status:** In Specification  

---

## 1. Module Overview & Objective
{mod_desc}

---

## 2. Granular Functional Requirements
{reqs_formatted}

---

## 3. Architecture & Key Files Impacted
- Implementation scripts and templates will reside inside or be referenced by this module.
- Validation checks and unit tests will log results directly to this folder.

---

## 4. Verification Checklist
- [ ] Requirements implemented without breaking existing views
- [ ] Automated syntax and Django check passed
- [ ] UI and responsiveness verified on mobile and desktop
"""
        speckit_file.write_text(content, encoding='utf-8')
        print(f"Created Module: {phase_dir}/{mod_dir}/speckit.md")

print(f"\nSuccessfully generated {count_modules} module directories with complete speckit.md files across all phases!")
