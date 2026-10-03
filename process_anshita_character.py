import os
from PIL import Image, ImageOps, ImageFilter

# Paths to generated high-res states
ARTIFACTS_DIR = r"C:\Users\Aksha\.gemini\antigravity-ide\brain\bae71adb-aa2a-4003-a463-e3b600c94f71"
DEST_DIR = r"f:\Code by Akshat\Anshita\anshitamakeover aiarena\workspace-01a06312-9f47-7052-a276-d661b1051b1c\django\core\static\core\images\brand"

os.makedirs(DEST_DIR, exist_ok=True)

raw_files = {
    "idle": os.path.join(ARTIFACTS_DIR, "anshita_3d_concierge_1790786567615.jpg"),
    "blink": os.path.join(ARTIFACTS_DIR, "anshita_3d_blink_1790786593412.jpg"),
    "talk": os.path.join(ARTIFACTS_DIR, "anshita_3d_talk_1790786617601.jpg"),
}

for state, filepath in raw_files.items():
    if not os.path.exists(filepath):
        print(f"Error: {filepath} does not exist!")
        continue
    
    img = Image.open(filepath).convert("RGBA")
    w, h = img.size
    
    # 1. Precise crop centered on face & bust
    # Coordinates: center x=0.5, face center y=0.45
    crop_size = min(w, h)
    # Give a bit of margin so the royal maang tikka and dupatta drape look majestic
    left = (w - crop_size) // 2
    top = int(h * 0.04)
    right = left + crop_size
    bottom = top + crop_size
    
    cropped = img.crop((left, top, right, bottom))
    resized = cropped.resize((512, 512), Image.Resampling.LANCZOS)
    
    # 2. Create smooth circular / feathered alpha vignette for 3D stage
    mask = Image.new("L", (512, 512), 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.ellipse((8, 8, 504, 504), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=6))
    
    # Apply alpha mask
    final_img = resized.copy()
    final_img.putalpha(mask)
    
    out_path = os.path.join(DEST_DIR, f"anshita_3d_{state}.png")
    final_img.save(out_path, "PNG", optimize=True)
    print(f"Processed and saved: {out_path} ({final_img.size})")

print("All Anshita 3D Concierge textures processed successfully!")
