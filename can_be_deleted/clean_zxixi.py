import re
import fitz

with open('../uploads/ZXiXi01.svg', 'r', encoding='utf-8') as f:
    text = f.read()

paths = re.findall(r'<path d="([^"]+)"', text)

clean_paths = []
face_only_paths = []

for idx, p in enumerate(paths):
    # Check if edge noise
    if 'M598' in p[:10] or ' 13 c' in p[:20] or 'M1785 1300' in p[:20]:
        continue
    clean_paths.append(f'<path d="{p}"/>')
    # If not outer ring (Path 1, Path 2) and not bottom text (idx >= 55)
    if idx > 2 and idx < 55:
        face_only_paths.append(f'<path d="{p}"/>')

print(f"Total paths: {len(paths)}, clean: {len(clean_paths)}, face only: {len(face_only_paths)}")

# 1. Full clean version of ZXiXi01 (in gold & currentColor)
clean_svg = f'''<svg version="1.0" xmlns="http://www.w3.org/2000/svg"
 width="600pt" height="600pt" viewBox="0 0 600 600"
 preserveAspectRatio="xMidYMid meet">
<g transform="translate(0,600) scale(0.1,-0.1)" fill="currentColor" stroke="none">
{''.join(clean_paths)}
</g>
</svg>'''

with open('core/static/core/images/brand/zxixi_cleaned.svg', 'w', encoding='utf-8') as f:
    f.write(clean_svg)

# Render clean preview
doc = fitz.open('core/static/core/images/brand/zxixi_cleaned.svg')
page = doc.load_page(0)
pix = page.get_pixmap(dpi=150)
pix.save('core/static/core/images/brand/zxixi_cleaned_render.png')
print("Rendered zxixi_cleaned_render.png")
