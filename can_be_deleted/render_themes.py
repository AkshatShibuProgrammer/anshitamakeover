import os
import cairosvg

with open('anshita_project/core/static/core/images/brand/sinha_royal_c2_crest.svg', 'r', encoding='utf-8') as f:
    svg_body = f.read().split('<svg viewBox="0 0 1000 1020" xmlns="http://www.w3.org/2000/svg">')[1]

themes = [
    ('obsidian', '#080707', '#D4AF37'),
    ('maroon', '#1B0910', '#F7E7A9'),
    ('emerald', '#061811', '#E6D5AC'),
    ('white', '#FFFFFF', '#18181B')
]

for name, bg, fg in themes:
    content = f'''<svg viewBox="0 0 1000 1020" width="1000" height="1020" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="{bg}"/>
  <g color="{fg}">
    {svg_body}
'''
    temp_svg = f'anshita_project/core/static/core/images/brand/temp_{name}.svg'
    with open(temp_svg, 'w', encoding='utf-8') as tf:
        tf.write(content)
    
    png_out = f'anshita_project/core/static/core/images/brand/sinha_c2_{name}.png'
    cairosvg.svg2png(url=temp_svg, write_to=png_out, output_width=1000, output_height=1020)
    print(f'Rendered {png_out}')
    if os.path.exists(temp_svg):
        os.remove(temp_svg)
