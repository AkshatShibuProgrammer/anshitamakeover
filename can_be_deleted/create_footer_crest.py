import os

with open('anshita_project/core/static/core/images/brand/sinha_royal_c2_crest.svg', 'r', encoding='utf-8') as f:
    svg_body = f.read()

include_dir = 'anshita_project/core/templates/core/includes'
os.makedirs(include_dir, exist_ok=True)

footer_crest_html = f'''{{% load static %}}
<!-- THE SINHA FAMILY GROUP - CONCEPT 02 VECTOR CREST (24K GOLD) -->
<div class="sinha-footer-crest-wrapper" style="margin: 45px auto 30px auto; text-align: center; display: flex; flex-direction: column; align-items: center; position: relative; z-index: 10;">
  <div class="sinha-footer-crest-container" style="width: 135px; height: 135px; max-width: 25vw; color: #D4AF37; filter: drop-shadow(0 6px 20px rgba(212, 175, 55, 0.4)); transition: transform 0.4s ease, filter 0.4s ease; cursor: pointer;">
    {svg_body}
  </div>
  <div style="margin-top: 14px; font-family: 'Cinzel', serif; font-size: 0.82rem; letter-spacing: 4px; text-transform: uppercase; color: #D4AF37; font-weight: 600;">
    The Sinha Family Group
  </div>
  <div style="font-size: 0.68rem; letter-spacing: 2.5px; text-transform: uppercase; color: rgba(245, 237, 214, 0.55); margin-top: 5px;">
    Royal Patronage &bull; Legacy Heritage
  </div>
</div>

<style>
.sinha-footer-crest-container:hover {{
  transform: scale(1.08) translateY(-4px);
  filter: drop-shadow(0 10px 28px rgba(212, 175, 55, 0.7));
}}
</style>
'''

target_path = os.path.join(include_dir, 'sinha_c2_footer_crest.html')
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(footer_crest_html)

print('sinha_c2_footer_crest.html created successfully!')
