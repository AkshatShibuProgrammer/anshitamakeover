import re
import fitz
import math

with open('../uploads/ZXiXi01.svg', 'r', encoding='utf-8') as f:
    text = f.read()

paths = re.findall(r'<path d="([^"]+)"', text)

# Extract only face paths (indexes 3 to 54, excluding noise)
face_paths = []
for idx, p in enumerate(paths):
    if idx > 2 and idx < 55:
        if 'M598' in p[:10] or ' 13 c' in p[:20] or 'M1785 1300' in p[:20]:
            continue
        face_paths.append(f'<path d="{p}"/>')

# ZXiXi01 coordinate space for faces:
# In potrace coords (0 to 6000 x, 0 to 6000 y)
# The face bounding box is roughly x: [800, 5200], y: [1300, 4600]
# With scale(0.1, -0.1) and translate(0, 600), faces are in [80, 520] x and [140, 470] y.
# Center of faces is approx (300, 305).
# In our Royal Crest SVG viewBox="0 0 1000 1000", medallion center is (500, 510), inner radius is ~240 (diameter ~480).
# So to place ZXiXi01 faces into (500, 510):
# We scale ZXiXi01 face group by 0.95:
# Center translation:
# cx_orig = 300, cy_orig = 305
# In target: 500 = tx + 300 * s  => tx = 500 - 300 * 0.92 = 224
# 510 = ty + 305 * s  => ty = 510 - 305 * 0.92 = 229

# Beaded pearls: 84 pearls around circle cx=500, cy=510, r=268
dots = []
for i in range(84):
    angle = 2 * math.pi * i / 84
    x = 500 + 268 * math.cos(angle)
    y = 510 + 268 * math.sin(angle)
    dots.append(f'      <circle cx="{x:.2f}" cy="{y:.2f}" r="2.6" fill="currentColor"/>')
dots_svg = '\n'.join(dots)

# Sunburst radial hatch marks: r1=250 to r2=258/254
rays = []
for i in range(120):
    angle = 2 * math.pi * i / 120
    x1 = 500 + 248 * math.cos(angle)
    y1 = 510 + 248 * math.sin(angle)
    r2 = 258 if i % 2 == 0 else 254
    x2 = 500 + r2 * math.cos(angle)
    y2 = 510 + r2 * math.sin(angle)
    rays.append(f'      <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="currentColor" stroke-width="1.2" opacity="0.6"/>')
rays_svg = '\n'.join(rays)

# Laurel wreath leaves cradling the lower half of the medallion
leaves = []
for side in [-1, 1]:
    for i in range(13):
        t = (i + 1) / 14.0
        ang = math.pi/2 + side * (0.16 + t * 1.30)
        r_arc = 282 + t * 6
        lx = 500 + r_arc * math.cos(ang)
        ly = 510 + r_arc * math.sin(ang)
        rot = (ang * 180 / math.pi) + (90 if side > 0 else -90)
        leaves.append(f'      <g transform="translate({lx:.2f}, {ly:.2f}) rotate({rot:.2f})"><path d="M 0 0 C -7 -14, -1 -24, 0 -30 C 1 -24, 7 -14, 0 0 Z" fill="currentColor" opacity="0.95"/></g>')
        bx = 500 + (r_arc - 9) * math.cos(ang)
        by = 510 + (r_arc - 9) * math.sin(ang)
        leaves.append(f'      <circle cx="{bx:.2f}" cy="{by:.2f}" r="2.2" fill="currentColor"/>')
leaves_svg = '\n'.join(leaves)

# Crown paths (Imperial crown atop medallion)
crown_svg = '''  <!-- IMPERIAL ROYAL CROWN (CONCEPT 02 STYLE) -->
  <g id="imperial-crown">
    <!-- Finial Cross & Orb -->
    <path d="M 500 95 L 500 125 M 487 108 L 513 108" stroke="currentColor" stroke-width="4.5" stroke-linecap="square"/>
    <circle cx="500" cy="128" r="6.5" fill="currentColor"/>
    
    <!-- Velvety Cap Lining -->
    <path d="M 500 132 C 452 140, 412 175, 418 228 C 448 223, 478 221, 500 221 C 522 221, 552 223, 582 228 C 588 175, 548 140, 500 132 Z" fill="none" stroke="currentColor" stroke-width="2" opacity="0.35"/>
    
    <!-- Outer Ribbed Arches -->
    <path d="M 500 132 C 455 156, 425 192, 420 228" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round"/>
    <path d="M 500 132 C 545 156, 575 192, 580 228" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round"/>
    <!-- Inner Ribbed Arches -->
    <path d="M 500 132 C 478 160, 462 195, 462 228" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>
    <path d="M 500 132 C 522 160, 538 195, 538 228" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="500" y1="132" x2="500" y2="228" stroke="currentColor" stroke-width="4.5" stroke-linecap="round"/>

    <!-- Pearls on central arch -->
    <circle cx="500" cy="148" r="3" fill="currentColor"/>
    <circle cx="500" cy="164" r="3" fill="currentColor"/>
    <circle cx="500" cy="180" r="3" fill="currentColor"/>
    <circle cx="500" cy="196" r="3" fill="currentColor"/>
    <circle cx="500" cy="212" r="3" fill="currentColor"/>
    
    <!-- Fleur-de-lis and Trefoils -->
    <path d="M 500 205 C 496 215, 491 221, 486 226 C 493 227, 500 227, 507 226 C 502 221, 497 215, 500 205 Z" fill="currentColor"/>
    <path d="M 500 205 C 489 211, 479 213, 476 223 C 484 223, 491 220, 496 215 Z" fill="currentColor"/>
    <path d="M 500 205 C 511 211, 521 213, 524 223 C 516 223, 509 220, 504 215 Z" fill="currentColor"/>
    
    <path d="M 432 214 C 430 221, 427 225, 424 228 C 429 229, 434 229, 440 228 C 436 225, 433 221, 432 214 Z" fill="currentColor"/>
    <circle cx="432" cy="210" r="2.8" fill="currentColor"/>

    <path d="M 568 214 C 570 221, 573 225, 576 228 C 571 229, 566 229, 560 228 C 564 225, 567 221, 568 214 Z" fill="currentColor"/>
    <circle cx="568" cy="210" r="2.8" fill="currentColor"/>

    <circle cx="464" cy="221" r="3.5" fill="currentColor"/>
    <circle cx="536" cy="221" r="3.5" fill="currentColor"/>

    <!-- Crown Circlet Band -->
    <path d="M 412 233 C 445 226, 555 226, 588 233 L 586 248 C 555 241, 445 241, 414 248 Z" fill="currentColor"/>
    <path d="M 411 251 C 445 244, 555 244, 589 251" fill="none" stroke="currentColor" stroke-width="1.8"/>
    
    <!-- Gemstone Cutouts -->
    <circle cx="428" cy="240" r="3.2" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <polygon points="452,235 458,240 452,245 446,240" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <circle cx="476" cy="240" r="3.2" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <polygon points="500,234 507,240 500,246 493,240" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <circle cx="524" cy="240" r="3.2" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <polygon points="548,235 554,240 548,245 542,240" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <circle cx="572" cy="240" r="3.2" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
  </g>'''

# Baroque Acanthus Scrollwork surrounding the medallion
scrollwork_svg = '''  <!-- BAROQUE ACANTHUS SCROLLWORK (CONCEPT 02 STYLE) -->
  <g id="baroque-scrollwork">
    <g id="flourish-half">
      <path d="M 408 245 C 370 225, 325 230, 305 265 C 290 290, 297 325, 323 340 C 345 352, 370 342, 375 328 C 380 314, 367 302, 353 306 C 340 310, 337 322, 345 328 C 337 328, 327 318, 329 304 C 333 280, 363 265, 397 274" fill="none" stroke="currentColor" stroke-width="3.8" stroke-linecap="round"/>
      <path d="M 305 265 C 275 260, 238 285, 233 320 C 241 312, 253 310, 265 315 C 253 325, 245 340, 248 362 C 258 350, 273 345, 285 350 C 271 365, 268 385, 275 408 C 288 390, 305 385, 318 392 C 303 412, 305 435, 315 460 C 328 438, 345 435, 361 440 C 345 460, 347 488, 363 515 C 375 490, 393 485, 408 490" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
      <path d="M 233 320 C 212 340, 207 375, 222 402 C 234 422, 260 430, 274 415 C 284 404, 280 386, 267 385 C 254 384, 246 396, 252 405" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/>
      <path d="M 222 402 C 196 430, 193 475, 213 512 C 231 542, 266 555, 296 538 C 313 528, 316 508, 301 500 C 289 492, 276 502, 281 515" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/>
      <path d="M 213 512 C 191 550, 196 605, 231 645 C 261 680, 311 695, 356 675 C 381 662, 386 640, 369 630 C 353 620, 339 632, 346 648" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
    </g>
    <use href="#flourish-half" transform="translate(1000, 0) scale(-1, 1)"/>
  </g>'''

# Medallion frame assembly
medallion_frame = f'''  <!-- CENTRAL MEDALLION FRAME (CONCEPT 02 STYLE) -->
  <g id="medallion-frame">
    <!-- Outer Heavy Molded Rim -->
    <circle cx="500" cy="510" r="285" fill="none" stroke="currentColor" stroke-width="5.5"/>
    <circle cx="500" cy="510" r="278" fill="none" stroke="currentColor" stroke-width="1.8"/>
    
    <!-- Beaded Ring of 84 Pearls -->
    <g id="beaded-pearls">
{dots_svg}
    </g>
    
    <!-- Inner Rings -->
    <circle cx="500" cy="510" r="258" fill="none" stroke="currentColor" stroke-width="2.8"/>
    <circle cx="500" cy="510" r="250" fill="none" stroke="currentColor" stroke-width="1.6"/>
    
    <!-- Radial Rays -->
    <g id="sunburst-rays">
{rays_svg}
    </g>
    
    <circle cx="500" cy="510" r="242" fill="none" stroke="currentColor" stroke-width="2.2"/>

    <!-- Laurel Wreath Cradling the Base -->
    <g id="laurel-wreath">
      <path d="M 492 780 C 484 790, 474 796, 464 792 C 454 788, 458 776, 470 774 C 484 772, 492 776, 498 780" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <path d="M 508 780 C 516 790, 526 796, 536 792 C 546 788, 542 776, 530 774 C 516 772, 508 776, 502 780" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <circle cx="500" cy="780" r="4.2" fill="currentColor"/>
{leaves_svg}
    </g>
  </g>'''

# Place ZXiXi01 face paths into the medallion:
# We wrap them in their native transform scale(0.1, -0.1) translate(0, 600)
# and then outer scale/translate to fit cx=500, cy=510:
# Bounding box center in 600x600 space is (300, 310).
# We want this center at (500, 510) with size scaled to ~420px (scale = 420 / 460 = 0.91):
# translate(500, 510) scale(0.91) translate(-300, -310)
faces_placed = f'''  <!-- EMBEDDED USER UPLOADED (ZXIXI01) VECTOR FACES -->
  <g id="zxixi-faces" transform="translate(500, 515) scale(0.88) translate(-300, -310)">
    <g transform="translate(0,600) scale(0.1,-0.1)" fill="currentColor" stroke="none">
{''.join(face_paths)}
    </g>
    <!-- Add Authentic Tilak & Bindi in Red -->
    <path d="M 233 226 C 230 236, 230 248, 233 255 C 237 248, 237 236, 233 226 Z" fill="#D9383A"/>
    <circle cx="363" cy="288" r="4" fill="#D9383A"/>
  </g>'''

# Straight, clean brand typography:
typography = '''  <!-- LUXURY STRAIGHT TYPOGRAPHY (NO CURVE, NO SINHA RIBBON, NO EST YEAR) -->
  <g id="brand-typography" transform="translate(500, 885)" text-anchor="middle">
    <!-- Star Insignia Divider -->
    <path d="M 0 -22 L 3 -13 L 12 -10 L 3 -7 L 0 2 L -3 -7 L -12 -10 L -3 -13 Z" fill="currentColor"/>
    <line x1="-180" y1="-10" x2="-25" y2="-10" stroke="currentColor" stroke-width="1.6" opacity="0.65"/>
    <line x1="25" y1="-10" x2="180" y2="-10" stroke="currentColor" stroke-width="1.6" opacity="0.65"/>
    <circle cx="-180" cy="-10" r="2.8" fill="currentColor"/>
    <circle cx="180" cy="-10" r="2.8" fill="currentColor"/>

    <!-- Primary Brand Title -->
    <text y="24" font-family="'Cinzel', 'Trajan Pro', 'Baskerville', serif" font-size="34" font-weight="700" letter-spacing="10" fill="currentColor">THE SINHA FAMILY GROUP</text>

    <!-- Subtitle Line -->
    <text y="56" font-family="'Montserrat', 'Helvetica Neue', sans-serif" font-size="13" font-weight="500" letter-spacing="6" fill="currentColor" opacity="0.85">HERITAGE · TRANSCENDENCE · UNITY</text>
    <line x1="-90" y1="74" x2="90" y2="74" stroke="currentColor" stroke-width="1.2" opacity="0.45"/>
  </g>'''

full_svg = f'''<svg viewBox="0 0 1000 1000" xmlns="http://www.w3.org/2000/svg">
{crown_svg}
{scrollwork_svg}
{medallion_frame}
{faces_placed}
{typography}
</svg>
'''

with open('core/static/core/images/brand/sinha_royal_c2_crest.svg', 'w', encoding='utf-8') as out:
    out.write(full_svg)

print('SUCCESS: Generated sinha_royal_c2_crest.svg with ZXiXi01 faces! Size:', len(full_svg))

# Render preview
doc = fitz.open('core/static/core/images/brand/sinha_royal_c2_crest.svg')
page = doc.load_page(0)
pix = page.get_pixmap(dpi=150)
pix.save('core/static/core/images/brand/sinha_royal_c2_crest_render.png')
print('Rendered sinha_royal_c2_crest_render.png')
