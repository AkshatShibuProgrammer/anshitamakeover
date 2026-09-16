import re

with open('../uploads/ZXiXi01.svg', 'r', encoding='utf-8') as f:
    text = f.read()

paths = re.findall(r'<path d="([^"]+)"', text)
print('Total paths:', len(paths))
for i, m in enumerate(paths):
    tokens = m.split()
    print(f"Path {i:2d}: tokens={len(tokens):5d}, start={m[:50]}")
