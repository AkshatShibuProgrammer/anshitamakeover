import re
import fitz

with open('../uploads/ZXiXi01.svg', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect paths
paths = re.findall(r'<path d="([^"]+)"', text)
print(f'Total paths in ZXiXi01.svg: {len(paths)}')

# Let's check the bounding box of each path
# Notice the transform: scale(0.1, -0.1) translate(0, 600)
# So standard x = X * 0.1, standard y = 600 - Y * 0.1

results = []
for idx, p in enumerate(paths):
    tokens = p.replace(',', ' ').split()
    nums = []
    for t in tokens:
        try:
            nums.append(float(t))
        except ValueError:
            pass
    if len(nums) >= 4:
        xs = nums[0::2]
        ys = nums[1::2]
        min_x, max_x = min(xs)*0.1, max(xs)*0.1
        min_y, max_y = 600 - max(ys)*0.1, 600 - min(ys)*0.1
        results.append((idx, len(p), min_x, max_x, min_y, max_y))

for r in results[:15]:
    print(f"Path {r[0]:2d}: len={r[1]:5d} x=[{r[2]:.1f}, {r[3]:.1f}] y=[{r[4]:.1f}, {r[5]:.1f}]")

# Let's check artifacts/specks (tiny paths)
tiny_paths = [r for r in results if (r[3]-r[2]) < 5 and (r[5]-r[4]) < 5]
print(f"Tiny speck paths (<5px): {len(tiny_paths)}")

# Let's check text paths (at the bottom, y > 500)
text_paths = [r for r in results if r[4] > 500]
print(f"Bottom text paths (y > 500): {len(text_paths)}")

# Main circular frame paths
frame_paths = [r for r in results if (r[3]-r[2]) > 400 and (r[5]-r[4]) > 400]
print(f"Circular frame paths: {len(frame_paths)}")
for fp in frame_paths:
    print(f"  Frame path {fp[0]}: len={fp[1]} x=[{fp[2]:.1f}, {fp[3]:.1f}] y=[{fp[4]:.1f}, {fp[5]:.1f}]")
