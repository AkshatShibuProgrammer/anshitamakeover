# Copyable prompt: Anshita Makeover second-AI website review

> You are an independent senior luxury digital-experience designer, mobile UX reviewer, Three.js/WebGL technical art director, accessibility reviewer, and technical SEO specialist. This is a **research and recommendation task only**. Do not edit code or claim to have implemented anything.
>
> ## Project and links
>
> Review the Anshita Makeover website, its current audit/planning documents, and the reference websites below. First verify whether the live site is reachable at **https://anshitamakeover.com/**; this domain is recorded in project documents but must be confirmed as the current canonical site. The public repository is **https://github.com/AkshatShibuProgrammer/anshitamakeover**. Its current working-tree changes may be uncommitted and therefore absent from GitHub. Do not say you reviewed local changes unless I attach the current files or diff.
>
> **Reference URLs recorded in the project documents:**
>
> - Evagher: https://evagher.com/ and https://evagher.com/en — project notes explicitly identify Evagher as the core reference shared by the owner.
> - Apple AirPods Pro: https://www.apple.com/airpods-pro/
> - Apple Vision Pro: https://www.apple.com/apple-vision-pro/
> - Gucci: https://www.gucci.com/
> - Dior: https://www.dior.com/
> - Stripe Press: https://press.stripe.com/
> - Bruno Simon: https://bruno-simon.com/
> - Duolingo: https://www.duolingo.com/
> - Awwwards: https://www.awwwards.com/
> - The FWA: https://thefwa.com/
> - Godly: https://godly.website/
> - Sabyasachi: https://www.sabyasachi.com/
> - Local/Indian bridal-business references listed in a project audit: https://www.instagram.com/dreammakeoversbykavya/ and https://www.facebook.com/aanchalsingraha2/
> - Vogue India bridal-artist article listed in that audit: https://www.vogue.in/beauty/content/top-indian-bridal-makeup-artists-you-should-follow-on-instagram-for-some-serious-inspiration
> - Anshita Makeover's Instagram profile, for first-party portfolio context: https://www.instagram.com/anshitamakeover21/
>
> The links above come from the repository's project/audit documents. Evagher is explicitly identified there as owner-shared; do not claim the owner personally supplied every other link. Treat all links as leads: inspect the current live pages, cite direct URLs, record the review date, and distinguish what you directly observed from what an older project document says. Awwwards, FWA and Godly are inspiration directories, not single-site design benchmarks.
>
> ## Latest owner instructions — these override older project notes
>
> - The protected animation is the opening **“Anshita Makeover” sequence before entering the studio**. It is perfect. **Do not change, replace, retime, restyle, hide, or redesign this sequence.** Recommend changes around it only, and identify a way to check it has not changed.
> - Preferred visual direction: **couture editorial**, retaining the current brand identity but making the presentation calmer, clearer and more premium. Start with the homepage and shared mobile shell; do not propose a wholesale rebrand by default.
> - Mochi is the rabbit and should be selected by default; Pip is the bird and should remain selectable. The owner wants the actual 3D character from **`3d character for anshitamakeover/`**, not a flat image and not an unrelated replacement. The earlier owner handoff identifies `index-expressions.html` as the intended Mochi/Pip reference; inspect it as the working source and do not swap to demo GLBs or another character. If you find evidence the owner means a different file, ask rather than substitute.
> - The owner wants **proper 3D physical motion**. Explain what is appropriate: grounded foot/paw contact, believable gait, acceleration/inertia, and restrained ear/wing/tail secondary motion. Clearly distinguish deterministic rig animation with physical-looking secondary motion from a full rigid-body physics simulation; do not add or promise a physics engine without evidence it is needed.
> - The owner named **Jabalpur, Bhopal, Indore and Lucknow** as service-area cities. Do not reinstate broader city or “all India” claims from older files without confirmation. Ask or clearly flag which named cities are regular service versus destination-by-enquiry.
> - Preferred city treatment: a restrained one-city-at-a-time rotator with pause/next controls and a reduced-motion static state, plus accurate visible coverage details. No hidden city text, keyword stuffing or thin doorway pages.
> - Preserve the existing chatbot and security posture. Do not remove chatbot behavior or expose credentials. The owner does not know the admin route/customization; inspect the source to map routes and explain any risk without requesting passwords or other secrets. Production reachability cannot be inferred from source alone.
> - Keep G8 strict: **fewer than 25 draw calls**. Do not relax the limit. Prefer one live 3D rig at a time unless a faithful option proves it remains under the gate.
> - The owner confirms the current homepage CTA destinations are correct: “Explore Lookbook” goes to Gallery, and “Book on WhatsApp” opens WhatsApp. Preserve these actions; do not redirect a homepage CTA back to the homepage.
>
> ## Materials to inspect
>
> If available, review and cite the relevant evidence in:
>
> - `docs/PLAN_AUDIT_AND_GAP_ANALYSIS.md`
> - `docs/PROFESSIONAL_WEBSITE_REFINEMENT_PLAN.md`
> - `docs/COMPREHENSIVE_3D_MASCOT_ANIMATION_AND_SECURITY_AUDIT.md`
> - `docs/ANIMATION_SPECIFICATION.md`
> - `docs/MASCOT_WALK_AND_SCROLL_GAP_ANALYSIS.md`
> - `docs/MOBILE_AND_MASCOT_GAP_ANALYSIS.md`
> - `3d character for anshitamakeover/` (especially the relevant Mochi/Pip source and current previews)
> - Current desktop/mobile screenshots and any local diff/files supplied by the owner.
>
> Older project files may describe another character source, more cities, or historical behavior. Follow the latest owner instructions above; mark discrepancies instead of quietly choosing an interpretation. If you cannot access the repository's local files, say so and request them.
>
> ## Review work
>
> 1. Research **6–10 current live reference sites** relevant to premium beauty/bridal, fashion/editorial storytelling, or thoughtful 3D/motion. Include the provided leads but add more only when they are relevant. Cite each site and say what you actually observed. Inspect desktop and mobile where possible; do not repeat old audit claims without checking them.
> 2. Review the live Anshita Makeover website if reachable and the supplied source/audit. Separate production observations from source-tree facts and stale screenshots. Use viewport notes (at least 1440×900, 390×844 and a narrower phone width where possible).
> 3. Identify the biggest professionalism gaps by page: home, services/service details, packages, gallery/albums, booking/cart, travel estimator, chatbot and Academy. Tie each critique to a specific section or file when evidence permits.
> 4. Provide **three practical design/motion options** with trade-offs and mark one recommendation. Preserve the protected intro animation in all options. Include a simple homepage storyboard for Mochi/Pip and a separate mobile composition.
> 5. Explain how the selected 3D-folder Mochi can be used without turning it into a 2D image or replacing it. Identify the exact candidate source file(s), animation/rig capabilities and missing pieces. Recommend physically believable movement while retaining scroll reversibility, stable floor contact, accessibility and performance.
> 6. Recommend a truthful, accessible city rotator and page content architecture for Jabalpur, Bhopal, Indore and Lucknow. Flag any facts that need owner confirmation. Do not promise rankings or invent local details.
> 7. Review current Google SEO and AI/agentic discoverability using current, authoritative sources. Separate verified platform guidance from speculation. Check crawlable visible text, canonical pages, local business facts/schema, metadata, sitemap/internal links, performance and accessibility. State when Search Console, Analytics, server logs or business records would be needed.
> 8. Review security issues only from safe, authorized evidence. Map the relevant source routes and explain what must be verified in production, but do not attempt intrusive probing, request credentials, or reproduce secrets.
>
> ## Required response format
>
> - Executive verdict (short).
> - Prioritized **step-by-step plan** with deliverables and approval gates.
> - Options table: each option's visual/motion approach, desktop/mobile behavior, benefit, risk, effort and test.
> - Page-by-page improvement list.
> - Mochi/Pip storyboard and technical notes on the selected 3D source and physical motion.
> - City/SEO proposal and unresolved owner facts.
> - A short list of questions; ask only what blocks a safe decision.
> - A reference list with working URLs and the review date.
>
> Be specific and candid. Avoid generic advice such as “add more animation,” “switch to React,” “use AI SEO,” or “make everything gold.” Do not change code. Do not alter the protected opening animation. Keep the review separate from implementation; the owner will discuss your findings with the coding agent first.
