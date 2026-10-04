import os
import sys
from pathlib import Path
import json

def extract_frames():
    try:
        import cv2
    except ImportError:
        print("ERROR: opencv-python (cv2) is not installed.")
        return False

    base_dir = Path(__file__).resolve().parent.parent
    video_dir = base_dir / "django" / "core" / "static" / "core" / "videos"
    output_dir = base_dir / "django" / "core" / "static" / "core" / "images" / "transformation_frames"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prefer royal_velvet_bride_muted or eyes_makeup_40s
    candidates = [
        video_dir / "royal_velvet_bride_muted.mp4",
        video_dir / "eyes_makeup_40s.mp4",
        video_dir / "VID-20250804-WA0177_muted.mp4"
    ]

    selected_video = None
    for c in candidates:
        if c.exists() and c.stat().st_size > 0:
            selected_video = c
            break

    if not selected_video:
        print("ERROR: No valid candidate video found in", video_dir)
        return False

    print(f"Extracting frames from: {selected_video.name} ({selected_video.stat().st_size / (1024*1024):.1f} MB)")

    cap = cv2.VideoCapture(str(selected_video))
    if not cap.isOpened():
        print(f"ERROR: Cannot open video {selected_video}")
        return False

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_s = total_frames / fps if fps > 0 else 0

    print(f"Video Stats: {total_frames} frames, {fps:.1f} FPS, {width}x{height}, {duration_s:.1f}s")

    # Sample exactly 48 clean frames across the duration
    target_count = 48
    step = max(1, total_frames // target_count)
    extracted_paths = []

    # Calculate target dimensions (e.g., width 800, keep aspect ratio)
    target_w = 800
    target_h = int(height * (target_w / width))
    # Make sure height is even
    if target_h % 2 != 0:
        target_h += 1

    saved_idx = 0
    for i in range(0, total_frames, step):
        if saved_idx >= target_count:
            break
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            continue

        # Resize for web performance
        resized = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)

        filename = f"frame_{saved_idx:03d}.webp"
        out_path = output_dir / filename
        cv2.imwrite(str(out_path), resized, [cv2.IMWRITE_WEBP_QUALITY, 80])
        extracted_paths.append(f"/static/core/images/transformation_frames/{filename}")
        saved_idx += 1

    cap.release()

    meta = {
        "video_source": selected_video.name,
        "total_extracted": saved_idx,
        "frame_width": target_w,
        "frame_height": target_h,
        "frames": extracted_paths
    }

    meta_path = output_dir / "frames_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"SUCCESS: Extracted {saved_idx} frames to {output_dir}")
    print(f"Metadata written to {meta_path}")
    return True

if __name__ == "__main__":
    extract_frames()
