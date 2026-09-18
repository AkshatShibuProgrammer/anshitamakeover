import json
from pathlib import Path

sum_file = Path('temp/instagram_summary.json')
out_txt = Path('anshita_project/resources/instagram_media_links.txt')
out_txt.parent.mkdir(parents=True, exist_ok=True)

lines = [
    '================================================================================',
    '       ANSHITA MAKEOVER (@anshitamakeover21) — INSTAGRAM MEDIA REGISTRY         ',
    '================================================================================',
    'Profile: https://www.instagram.com/anshitamakeover21/',
    'Official Portfolio Links, Reels & Post Captions:\n'
]

if sum_file.exists():
    with open(sum_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for idx, p in enumerate(data.get('posts', [])):
        ptype = p.get('type', 'photo').upper()
        purl = p.get('instagram_url', '')
        pshort = p.get('shortcode', '')
        pthumb = p.get('thumbnail_file', '')
        pvid = p.get('video_file', '')
        caption = p.get('caption', '').replace('\n', ' ').strip()
        
        lines.append(f"[{idx+1}] TYPE: {ptype}")
        lines.append(f"    URL: {purl}")
        lines.append(f"    SHORTCODE: {pshort}")
        if pthumb:
            lines.append(f"    COVER IMAGE: {pthumb}")
        if pvid:
            lines.append(f"    VIDEO FILE: {pvid}")
        lines.append(f"    CAPTION: {caption}")
        lines.append('-' * 70)

out_txt.write_text('\n'.join(lines), encoding='utf-8')
print(f"Successfully generated {out_txt} with {len(lines)} lines.")
