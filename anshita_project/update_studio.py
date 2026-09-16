import os

with open('core/templates/core/sinha_logo_studio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Load sinha_royal_c2_crest.svg
with open('core/static/core/images/brand/sinha_royal_c2_crest.svg', 'r', encoding='utf-8') as f:
    c2_svg_content = f.read().strip()

# 1. Update the 4-Grid Royal Crest section to use C2 + ZXiXi01
old_heraldry_anchor = '<!-- ROYAL IMPERIAL HERALDRY: EXACT SAME FACES IN 24K ROYAL CRESTS -->'
heraldry_end_anchor = '<!-- Quick Background Buttons -->'

new_heraldry_section = '''<!-- ROYAL IMPERIAL HERALDRY (CONCEPT 02 + UPLOADED ZXiXi01 FACES) -->
  <div style="margin: 60px 0 28px; text-align: center;">
    <div style="display:inline-flex;align-items:center;gap:8px;padding:6px 18px;border-radius:20px;background:rgba(212,175,55,0.15);border:1px solid var(--gold);color:var(--gold);font-size:0.78rem;letter-spacing:3px;text-transform:uppercase;font-weight:700">
      👑 Concept 02 Royal Vector Crest (With ZXiXi01.svg) 👑
    </div>
    <h2 style="font-family:'Cinzel',serif;font-size:2.2rem;margin:12px 0 10px;background:linear-gradient(135deg,#FFF,var(--gold));-webkit-background-clip:text;-webkit-text-fill-color:transparent">
      Authentic Faces in Royal Concept 02 Heraldry
    </h2>
    <p style="font-size:0.92rem;color:rgba(245,237,214,0.85);max-width:860px;margin:0 auto;line-height:1.7">
      Built using the <strong>exact same vector contours from your uploaded <code>ZXiXi01.svg</code></strong>, framed within the majestic <strong>Concept 02 style</strong> (imperial arch crown, baroque acanthus flourishes, and laurel wreath). Straight luxury serif typography &mdash; <em>no curved ribbons, no curved SINHA, and no EST year</em>.
    </p>
  </div>

  <!-- 4-GRID ROYAL CREST SHOWCASE -->
  <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:24px;margin-bottom:50px">
    
    <!-- 1. Obsidian Black Royal Silk -->
    <div style="background:#070707;border:2px solid var(--gold);border-radius:20px;overflow:hidden;box-shadow:0 12px 36px rgba(0,0,0,0.8);display:flex;flex-direction:column">
      <div style="padding:14px 18px;border-bottom:1px solid rgba(212,175,55,0.25);display:flex;justify-content:space-between;align-items:center;background:rgba(212,175,55,0.08)">
        <span style="font-size:0.75rem;font-weight:700;letter-spacing:1px;color:#D4AF37">👑 01. ROYAL OBSIDIAN & 24K GOLD</span>
        <a href="/static/core/images/brand/sinha_c2_obsidian.svg" download style="font-size:0.68rem;padding:3px 8px;border-radius:8px;background:rgba(212,175,55,0.2);color:#FFF;text-decoration:none;border:1px solid rgba(212,175,55,0.4)">Download SVG</a>
      </div>
      <div style="padding:20px;background:#050505;display:flex;align-items:center;justify-content:center;flex:1">
        <img src="/static/core/images/brand/sinha_c2_obsidian.png" alt="Concept 02 ZXiXi01 Crest on Obsidian" style="width:100%;height:auto;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.7)">
      </div>
      <div style="padding:14px 18px;font-size:0.75rem;color:rgba(245,237,214,0.7);border-top:1px solid rgba(255,255,255,0.06)">
        Exact ZXiXi01 elder faces inside the Concept 02 imperial crown & acanthus heraldry on deep midnight obsidian black.
      </div>
    </div>

    <!-- 2. Royal Velvet Maroon -->
    <div style="background:#1B0910;border:2px solid rgba(247,231,169,0.4);border-radius:20px;overflow:hidden;box-shadow:0 12px 36px rgba(27,9,16,0.8);display:flex;flex-direction:column">
      <div style="padding:14px 18px;border-bottom:1px solid rgba(247,231,169,0.25);display:flex;justify-content:space-between;align-items:center;background:rgba(247,231,169,0.08)">
        <span style="font-size:0.75rem;font-weight:700;letter-spacing:1px;color:#F7E7A9">🍷 02. ROYAL VELVET MAROON</span>
        <a href="/static/core/images/brand/sinha_c2_maroon.svg" download style="font-size:0.68rem;padding:3px 8px;border-radius:8px;background:rgba(247,231,169,0.2);color:#FFF;text-decoration:none;border:1px solid rgba(247,231,169,0.4)">Download SVG</a>
      </div>
      <div style="padding:20px;background:#18060E;display:flex;align-items:center;justify-content:center;flex:1">
        <img src="/static/core/images/brand/sinha_c2_maroon.png" alt="Concept 02 ZXiXi01 Crest on Maroon" style="width:100%;height:auto;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.7)">
      </div>
      <div style="padding:14px 18px;font-size:0.75rem;color:rgba(247,231,169,0.75);border-top:1px solid rgba(247,231,169,0.15)">
        Imperial Indian wedding & hospitality aesthetic with authentic faces on traditional royal maroon velvet.
      </div>
    </div>

    <!-- 3. Deep Royal Emerald -->
    <div style="background:#061811;border:2px solid rgba(167,243,208,0.4);border-radius:20px;overflow:hidden;box-shadow:0 12px 36px rgba(6,24,17,0.8);display:flex;flex-direction:column">
      <div style="padding:14px 18px;border-bottom:1px solid rgba(167,243,208,0.25);display:flex;justify-content:space-between;align-items:center;background:rgba(167,243,208,0.08)">
        <span style="font-size:0.75rem;font-weight:700;letter-spacing:1px;color:#A7F3D0">🌲 03. DEEP EMERALD & GOLD</span>
        <a href="/static/core/images/brand/sinha_c2_emerald.svg" download style="font-size:0.68rem;padding:3px 8px;border-radius:8px;background:rgba(167,243,208,0.2);color:#FFF;text-decoration:none;border:1px solid rgba(167,243,208,0.4)">Download SVG</a>
      </div>
      <div style="padding:20px;background:#05140E;display:flex;align-items:center;justify-content:center;flex:1">
        <img src="/static/core/images/brand/sinha_c2_emerald.png" alt="Concept 02 ZXiXi01 Crest on Emerald" style="width:100%;height:auto;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.7)">
      </div>
      <div style="padding:14px 18px;font-size:0.75rem;color:rgba(167,243,208,0.75);border-top:1px solid rgba(167,243,208,0.15)">
        Prestigious Mayfair / private asset trust atmosphere on British racing emerald.
      </div>
    </div>

    <!-- 4. Pure Clean White / Ivory Parchment -->
    <div style="background:#FFFFFF;border:2px solid #D5C29D;border-radius:20px;overflow:hidden;box-shadow:0 12px 36px rgba(0,0,0,0.18);display:flex;flex-direction:column">
      <div style="padding:14px 18px;border-bottom:1px solid #EAE0D0;display:flex;justify-content:space-between;align-items:center;background:#FAF8F4">
        <span style="font-size:0.75rem;font-weight:700;letter-spacing:1px;color:#785A28">☀️ 04. EXECUTIVE CLEAN WHITE</span>
        <a href="/static/core/images/brand/sinha_c2_white.svg" download style="font-size:0.68rem;padding:3px 8px;border-radius:8px;background:#E8DCBE;color:#333;text-decoration:none;border:1px solid #CCC">Download SVG</a>
      </div>
      <div style="padding:20px;background:#FFFFFF;display:flex;align-items:center;justify-content:center;flex:1">
        <img src="/static/core/images/brand/sinha_c2_white.png" alt="Concept 02 ZXiXi01 Crest on White" style="width:100%;height:auto;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.08)">
      </div>
      <div style="padding:14px 18px;font-size:0.75rem;color:#666;border-top:1px solid #EAE0D0">
        Clean black line-art vector for executive letterheads, legal trusts, investor kits, and light mode websites.
      </div>
    </div>

  </div>

  <!-- INTERACTIVE PLAYGROUND FOR CONCEPT 02 ROYAL CREST -->
  <div style="background:rgba(212,175,55,0.05);border:1px solid rgba(212,175,55,0.3);border-radius:24px;padding:32px;margin-bottom:60px">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:20px;margin-bottom:24px">
      <div>
        <h3 style="font-family:'Cinzel',serif;color:#FFF;font-size:1.3rem;margin:0 0 6px">Interactive Concept 02 Vector Crest Simulator</h3>
        <p style="font-size:0.82rem;color:rgba(245,237,214,0.65);margin:0">Test any background color or scale in real-time. This is pure, responsive SVG code rendered directly in your browser.</p>
      </div>

      '''

# Replace from old_heraldry_anchor up to '<!-- Quick Background Buttons -->'
idx1 = content.find(old_heraldry_anchor)
idx2 = content.find(heraldry_end_anchor)

if idx1 != -1 and idx2 != -1:
    content = content[:idx1] + new_heraldry_section + content[idx2:]

# 2. Replace the SVG inside #svg-container with c2_svg_content
svg_container_start = content.find('<div id="svg-container"')
if svg_container_start != -1:
    svg_tag_start = content.find('<svg', svg_container_start)
    svg_tag_end = content.find('</svg>', svg_tag_start) + 6
    sim_text_start = content.find('<div id="sim-text"', svg_tag_end)
    sim_text_end = content.find('</div>', sim_text_start) + 6
    
    # In c2_svg_content, typography is already included inside the SVG itself!
    # So we replace both the inner SVG and remove the duplicate #sim-text block.
    content = content[:svg_container_start] + f'''<div id="svg-container" style="width:280px;height:auto;margin-bottom:14px;transition:all .3s ease">
        {c2_svg_content}
      </div>''' + content[sim_text_end:]

with open('core/templates/core/sinha_logo_studio.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('SUCCESS: Fully updated sinha_logo_studio.html with Concept 02 + ZXiXi01!')
