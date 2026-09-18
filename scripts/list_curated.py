import os
import glob
from PIL import Image

# Let's see what each WA image is by creating a small montage or printing info
images = glob.glob('core/static/core/images/curated/*.jpg') + glob.glob('core/static/core/images/authentic/*.jpg')
for img in sorted(images):
    print(img)
