import fitz

with open('core/static/core/images/brand/sinha_royal_c2_crest.svg', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace currentColor with #D4AF37
gold_svg = text.replace('currentColor', '#D4AF37')

# Add dark background rect
gold_svg = gold_svg.replace(
    '<svg viewBox="0 0 1000 1020" xmlns="http://www.w3.org/2000/svg">',
    '<svg viewBox="0 0 1000 1020" xmlns="http://www.w3.org/2000/svg">\n  <rect width="1000" height="1020" fill="#070707"/>'
)

with open('core/static/core/images/brand/sinha_royal_c2_crest_gold.svg', 'w', encoding='utf-8') as f:
    f.write(gold_svg)

doc = fitz.open('core/static/core/images/brand/sinha_royal_c2_crest_gold.svg')
page = doc.load_page(0)
pix = page.get_pixmap(dpi=150)
pix.save('core/static/core/images/brand/sinha_royal_c2_crest_gold_render.png')
print('Rendered dark & gold version successfully!')
