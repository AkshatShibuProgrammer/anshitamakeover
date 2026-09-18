import re

with open('rendered_dump.html', 'r', encoding='utf-8') as f:
    html = f.read()

matches = re.findall(r'onclick=[\'"](.*?)[\'"]', html)
print('Total onclicks:', len(matches))
peek = [m for m in matches if 'lookbook' in m or 'peek' in m or 'gal' in m]
for p in set(peek):
    print('  ', p)
