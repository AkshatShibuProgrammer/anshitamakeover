import cv2
import numpy as np

# Load clean faces
faces = cv2.imread('core/static/core/images/brand/c5_faces_clean.png', cv2.IMREAD_UNCHANGED)
alpha = faces[:, :, 3]
coords = cv2.findNonZero(alpha)
x, y, w, h = cv2.boundingRect(coords)
cropped = faces[y:y+h, x:x+w]
cv2.imwrite('core/static/core/images/brand/sinha_faces_cropped.png', cropped)

# Detect red marks (tilak & bindi)
hsv = cv2.cvtColor(cropped[:, :, :3], cv2.COLOR_BGR2HSV)
red_mask = (cv2.inRange(hsv, np.array([0, 70, 50]), np.array([10, 255, 255])) |
            cv2.inRange(hsv, np.array([170, 70, 50]), np.array([180, 255, 255]))) & (cropped[:, :, 3] > 40)

# Detect lines excluding red marks
gold_mask = (cropped[:, :, 3] > 35) & (~red_mask)

# Vectorize gold contours
gold_contours, _ = cv2.findContours(gold_mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
red_contours, _ = cv2.findContours(red_mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

print(f"Traced {len(gold_contours)} gold vector paths, {len(red_contours)} red vector paths. Bounding box: {w}x{h}")

def contour_to_d(c):
    approx = cv2.approxPolyDP(c, 0.8, True)
    pts = approx.reshape(-1, 2)
    if len(pts) < 3:
        return ""
    return f"M {pts[0][0]} {pts[0][1]} " + " ".join([f"L {p[0]} {p[1]}" for p in pts[1:]]) + " Z"

gold_paths = [contour_to_d(c) for c in gold_contours if contour_to_d(c)]
red_paths = [contour_to_d(c) for c in red_contours if contour_to_d(c)]

with open('core/static/core/images/brand/sinha_c5_faces_pure.svg', 'w') as f:
    f.write(f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">\n')
    f.write('  <g fill="currentColor">\n')
    for d in gold_paths:
        f.write(f'    <path d="{d}"/>\n')
    f.write('  </g>\n')
    f.write('  <g fill="#D9383A">\n')
    for d in red_paths:
        f.write(f'    <path d="{d}"/>\n')
    f.write('  </g>\n')
    f.write('</svg>\n')

print("Pure SVG generated: core/static/core/images/brand/sinha_c5_faces_pure.svg")
