import re
import fitz

with open('../uploads/ZXiXi01.svg', 'r', encoding='utf-8') as f:
    text = f.read()

paths = re.findall(r'<path d="([^"]+)"', text)

# Let's see what happens if we render Path 2 alone
p2_svg = f'''<svg version="1.0" xmlns="http://www.w3.org/2000/svg"
 width="600pt" height="600pt" viewBox="0 0 600 600">
<g transform="translate(0,600) scale(0.1,-0.1)" fill="#000000" stroke="none">
<path d="{paths[2]}"/>
</g>
</svg>'''

with open('core/static/core/images/brand/test_p2.svg', 'w') as f:
    f.write(p2_svg)

doc = fitz.open('core/static/core/images/brand/test_p2.svg')
page = doc.load_page(0)
pix = page.get_pixmap(dpi=150)
pix.save('core/static/core/images/brand/test_p2.png')
print("Rendered test_p2.png")
