import fitz

with open('core/static/core/images/brand/sinha_royal_c2_crest.svg', 'r', encoding='utf-8') as f:
    text = f.read()

themes = [
    ('obsidian', '#070707', '#D4AF37'),
    ('maroon', '#1B0910', '#F7E7A9'),
    ('emerald', '#061811', '#E6D5AC'),
    ('white', '#FFFFFF', '#18181B')
]

for name, bg, fg in themes:
    themed_svg = text.replace('currentColor', fg)
    themed_svg = themed_svg.replace(
        '<svg viewBox="0 0 1000 1020" xmlns="http://www.w3.org/2000/svg">',
        f'<svg viewBox="0 0 1000 1020" xmlns="http://www.w3.org/2000/svg">\n  <rect width="1000" height="1020" fill="{bg}"/>'
    )
    svg_path = f'core/static/core/images/brand/sinha_c2_{name}.svg'
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(themed_svg)
    
    doc = fitz.open(svg_path)
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=150)
    png_path = f'core/static/core/images/brand/sinha_c2_{name}.png'
    pix.save(png_path)
    print(f'Rendered {png_path} successfully!')
