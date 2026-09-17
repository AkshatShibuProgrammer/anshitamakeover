import re
import fitz
import math

with open('../uploads/ZXiXi01.svg', 'r', encoding='utf-8') as f:
    text = f.read()

paths = re.findall(r'<path d="([^"]+)"', text)

# Clean all paths of ZXiXi01 except the edge noise and the bottom text
medallion_paths = []
for idx, p in enumerate(paths):
    # Skip edge noise
    if 'M598' in p[:10] or ' 13 c' in p[:20] or 'M1785 1300' in p[:20]:
        continue
    # Skip bottom text (idx >= 55)
    if idx >= 55:
        continue
    medallion_paths.append(f'<path d="{p}"/>')

print(f"Total medallion paths from ZXiXi01: {len(medallion_paths)}")

# Crown paths (Imperial crown resting on the top of the medallion rim, center x=500, base y=238)
crown_svg = '''  <!-- IMPERIAL ROYAL CROWN (CONCEPT 02 STYLE) -->
  <g id="imperial-crown">
    <!-- Finial Cross & Orb -->
    <path d="M 500 85 L 500 118 M 485 100 L 515 100" stroke="currentColor" stroke-width="4.5" stroke-linecap="square"/>
    <circle cx="500" cy="122" r="6.5" fill="currentColor"/>
    
    <!-- Velvety Cap Lining -->
    <path d="M 500 126 C 452 134, 410 170, 416 226 C 448 221, 478 219, 500 219 C 522 219, 552 221, 584 226 C 590 170, 548 134, 500 126 Z" fill="none" stroke="currentColor" stroke-width="2" opacity="0.35"/>
    
    <!-- Outer Ribbed Arches -->
    <path d="M 500 126 C 455 150, 422 188, 416 226" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round"/>
    <path d="M 500 126 C 545 150, 578 188, 584 226" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round"/>
    <!-- Inner Ribbed Arches -->
    <path d="M 500 126 C 476 156, 460 192, 460 226" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>
    <path d="M 500 126 C 524 156, 540 192, 540 226" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="500" y1="126" x2="500" y2="226" stroke="currentColor" stroke-width="4.5" stroke-linecap="round"/>

    <!-- Pearls on central arch -->
    <circle cx="500" cy="142" r="3" fill="currentColor"/>
    <circle cx="500" cy="158" r="3" fill="currentColor"/>
    <circle cx="500" cy="174" r="3" fill="currentColor"/>
    <circle cx="500" cy="190" r="3" fill="currentColor"/>
    <circle cx="500" cy="206" r="3" fill="currentColor"/>
    
    <!-- Fleur-de-lis and Trefoils -->
    <path d="M 500 198 C 496 208, 491 214, 486 219 C 493 220, 500 220, 507 219 C 502 214, 497 208, 500 198 Z" fill="currentColor"/>
    <path d="M 500 198 C 489 204, 479 206, 476 216 C 484 216, 491 213, 496 208 Z" fill="currentColor"/>
    <path d="M 500 198 C 511 204, 521 206, 524 216 C 516 216, 509 213, 504 208 Z" fill="currentColor"/>
    
    <path d="M 430 208 C 428 215, 425 219, 422 222 C 427 223, 432 223, 438 222 C 434 219, 431 215, 430 208 Z" fill="currentColor"/>
    <circle cx="430" cy="204" r="2.8" fill="currentColor"/>

    <path d="M 570 208 C 572 215, 575 219, 578 222 C 573 223, 568 223, 562 222 C 566 219, 569 215, 570 208 Z" fill="currentColor"/>
    <circle cx="570" cy="204" r="2.8" fill="currentColor"/>

    <circle cx="462" cy="216" r="3.5" fill="currentColor"/>
    <circle cx="538" cy="216" r="3.5" fill="currentColor"/>

    <!-- Crown Circlet Band -->
    <path d="M 408 228 C 445 221, 555 221, 592 228 L 590 243 C 555 236, 445 236, 410 243 Z" fill="currentColor"/>
    <path d="M 407 246 C 445 239, 555 239, 593 246" fill="none" stroke="currentColor" stroke-width="1.8"/>
    
    <!-- Gemstone Cutouts -->
    <circle cx="424" cy="235" r="3.2" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <polygon points="448,230 454,235 448,240 442,235" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <circle cx="472" cy="235" r="3.2" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <polygon points="500,229 507,235 500,241 493,235" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <circle cx="528" cy="235" r="3.2" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <polygon points="552,230 558,235 552,240 546,235" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
    <circle cx="576" cy="235" r="3.2" fill="#080707" stroke="currentColor" stroke-width="1.2"/>
  </g>'''

# Baroque Acanthus Scrollwork surrounding the medallion
scrollwork_svg = '''  <!-- BAROQUE ACANTHUS SCROLLWORK FLOURISHES -->
  <g id="baroque-scrollwork">
    <g id="flourish-half">
      <!-- Upper Flourish Cresting -->
      <path d="M 408 240 C 365 218, 315 224, 290 262 C 274 288, 280 325, 308 342 C 332 355, 360 345, 366 328 C 372 312, 356 298, 340 302 C 326 306, 322 320, 332 328 C 322 328, 312 316, 314 300 C 319 272, 354 255, 394 266" fill="none" stroke="currentColor" stroke-width="4.2" stroke-linecap="round"/>
      
      <!-- Middle Acanthus Leaf Cascade -->
      <path d="M 290 262 C 255 256, 212 284, 206 324 C 215 315, 229 313, 242 318 C 228 330, 219 346, 222 372 C 234 358, 251 352, 265 358 C 249 375, 245 398, 253 424 C 268 404, 287 398, 302 406 C 285 428, 287 455, 299 482 C 314 458, 333 454, 351 460 C 333 482, 335 514, 353 544 C 367 516, 387 510, 404 516" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/>
      
      <!-- Lower Volute Curls -->
      <path d="M 206 324 C 182 346, 176 386, 193 416 C 206 438, 236 448, 252 431 C 263 419, 259 398, 244 397 C 230 396, 220 409, 227 419" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/>
      <path d="M 193 416 C 164 448, 160 498, 182 540 C 202 574, 242 588, 276 569 C 295 558, 298 535, 281 526 C 267 518, 253 529, 259 543" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/>
      <path d="M 182 540 C 157 582, 163 644, 202 688 C 236 726, 292 743, 342 721 C 370 706, 376 682, 357 671 C 339 660, 324 673, 332 691" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/>
    </g>
    <use href="#flourish-half" transform="translate(1000, 0) scale(-1, 1)"/>
  </g>'''

# Laurel wreath leaves cradling the bottom outer arc of the medallion
leaves = []
for side in [-1, 1]:
    for i in range(12):
        t = (i + 1) / 13.0
        ang = math.pi/2 + side * (0.18 + t * 1.15)
        r_arc = 276 + t * 6
        lx = 500 + r_arc * math.cos(ang)
        ly = 500 + r_arc * math.sin(ang)
        rot = (ang * 180 / math.pi) + (90 if side > 0 else -90)
        leaves.append(f'      <g transform="translate({lx:.2f}, {ly:.2f}) rotate({rot:.2f})"><path d="M 0 0 C -7 -14, -1 -24, 0 -30 C 1 -24, 7 -14, 0 0 Z" fill="currentColor" opacity="0.95"/></g>')
        bx = 500 + (r_arc - 9) * math.cos(ang)
        by = 500 + (r_arc - 9) * math.sin(ang)
        leaves.append(f'      <circle cx="{bx:.2f}" cy="{by:.2f}" r="2.4" fill="currentColor"/>')
leaves_svg = '\n'.join(leaves)

laurel_wreath = f'''  <!-- LAUREL WREATH CRADLING THE MEDALLION BASE -->
  <g id="laurel-wreath">
    <!-- Nadir Ribbon Knot -->
    <path d="M 492 762 C 484 772, 474 778, 464 774 C 454 770, 458 758, 470 756 C 484 754, 492 758, 498 762" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/>
    <path d="M 508 762 C 516 772, 526 778, 536 774 C 546 770, 542 758, 530 756 C 516 754, 508 758, 502 762" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/>
    <circle cx="500" cy="762" r="4.5" fill="currentColor"/>
{leaves_svg}
  </g>'''

# Place the entire ZXiXi01 medallion (faces + inner halo + collars) into the crest
# Centered at (500, 500), scaled by 1.20
# Original center in 600x600 space is (300, 310)
medallion_placed = f'''  <!-- COMPLETE AUTHENTIC MEDALLION FROM USER SVG (ZXIXI01) -->
  <g id="zxixi-medallion" transform="translate(500, 500) scale(1.20) translate(-300, -310)">
    <g transform="translate(0,600) scale(0.1,-0.1)" fill="currentColor" stroke="none">
{''.join(medallion_paths)}
    </g>
    <!-- Authentic Forehead Tilak & Bindi in Red -->
    <path d="M 233 226 C 230 236, 230 248, 233 255 C 237 248, 237 236, 233 226 Z" fill="#D9383A"/>
    <circle cx="363" cy="288" r="4.2" fill="#D9383A"/>
  </g>'''

# Centered luxury typography below the crest
# User command: "dont put est year or sinha at below curve"
# In SVG, text-anchor="middle" requires x="500" on the text elements so they center at 500!
typography = '''  <!-- LUXURY STRAIGHT TYPOGRAPHY (NO CURVE, NO SINHA RIBBON, NO EST YEAR) -->
  <g id="brand-typography">
    <!-- Star Insignia Divider -->
    <path d="M 500 863 L 503 872 L 512 875 L 503 878 L 500 887 L 497 878 L 488 875 L 497 872 Z" fill="currentColor"/>
    <line x1="320" y1="875" x2="475" y2="875" stroke="currentColor" stroke-width="1.6" opacity="0.65"/>
    <line x1="525" y1="875" x2="680" y2="875" stroke="currentColor" stroke-width="1.6" opacity="0.65"/>
    <circle cx="320" cy="875" r="2.8" fill="currentColor"/>
    <circle cx="680" cy="875" r="2.8" fill="currentColor"/>

    <!-- Primary Brand Title Centered at x=500 -->
    <text x="500" y="915" text-anchor="middle" font-family="'Cinzel', 'Trajan Pro', 'Baskerville', serif" font-size="34" font-weight="700" letter-spacing="10" fill="currentColor">THE SINHA FAMILY GROUP</text>

    <!-- Subtitle Line Centered at x=500 -->
    <text x="500" y="946" text-anchor="middle" font-family="'Montserrat', 'Helvetica Neue', sans-serif" font-size="13" font-weight="500" letter-spacing="6" fill="currentColor" opacity="0.85">HERITAGE · TRANSCENDENCE · UNITY</text>
    <line x1="410" y1="964" x2="590" y2="964" stroke="currentColor" stroke-width="1.2" opacity="0.45"/>
  </g>'''

full_svg = f'''<svg viewBox="0 0 1000 1020" xmlns="http://www.w3.org/2000/svg">
{crown_svg}
{scrollwork_svg}
{laurel_wreath}
{medallion_placed}
{typography}
</svg>
'''

with open('core/static/core/images/brand/sinha_royal_c2_crest.svg', 'w', encoding='utf-8') as out:
    out.write(full_svg)

print('SUCCESS: Updated sinha_royal_c2_crest.svg with centered typography! Size:', len(full_svg))

# Render preview
doc = fitz.open('core/static/core/images/brand/sinha_royal_c2_crest.svg')
page = doc.load_page(0)
pix = page.get_pixmap(dpi=150)
pix.save('core/static/core/images/brand/sinha_royal_c2_crest_render.png')
print('Rendered updated sinha_royal_c2_crest_render.png')
