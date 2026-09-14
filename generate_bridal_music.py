"""
Generates a soothing, royal Indian classical instrumental soundscape (Tanpura + Temple Chimes / Sitar Harmonics)
and uses imageio_ffmpeg to edit the Telegram bridal videos:
1. Creates a clean muted version (_muted.mp4)
2. Creates an ambient royal music version (_music.mp4)
"""
import os
import math
import wave
import struct
import subprocess
import imageio_ffmpeg
from pathlib import Path

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR = Path("temp/edited_videos")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_ambient_tanpura_wav(duration_sec=30, out_path="temp/bridal_ambience.wav"):
    sample_rate = 44100
    num_samples = int(duration_sec * sample_rate)
    
    # Tanpura C# tuning (Sa: 138.59 Hz, Pa: 207.65 Hz, High Sa: 277.18 Hz)
    frequencies = [
        (138.59, 0.25),  # Lower Sa
        (207.65, 0.20),  # Pa
        (277.18, 0.22),  # Sa
        (554.37, 0.08),  # Harmonic overtone
        (830.61, 0.04),  # Shimmer overtone
    ]
    
    # Chime notes in Raag Yaman (Sa, Re, Ga, Ma-tivra, Pa, Dha, Ni)
    chime_notes = [277.18, 311.13, 349.23, 392.00, 415.30, 466.16, 523.25, 554.37]
    
    print(f"[*] Generating {duration_sec}s serene bridal acoustic ambience...")
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        val = 0.0
        
        # Continuous undulating tanpura drone
        for freq, amp in frequencies:
            # Low frequency vibrato / pulsation
            lfo = 0.85 + 0.15 * math.sin(2 * math.pi * 0.3 * t + freq * 0.01)
            val += amp * lfo * math.sin(2 * math.pi * freq * t)
            
        # Periodic gentle temple chime bell notes every 3.5 seconds
        chime_cycle = t % 3.5
        chime_idx = int(t / 3.5) % len(chime_notes)
        chime_freq = chime_notes[chime_idx]
        if chime_cycle < 2.5:
            decay = math.exp(-chime_cycle * 2.2)
            chime_val = 0.18 * decay * (
                math.sin(2 * math.pi * chime_freq * t) +
                0.5 * math.sin(2 * math.pi * chime_freq * 2 * t) +
                0.25 * math.sin(2 * math.pi * chime_freq * 3 * t)
            )
            val += chime_val
            
        # Global smooth fade-in and fade-out
        fade_dur = 1.5
        if t < fade_dur:
            val *= (t / fade_dur)
        elif t > (duration_sec - fade_dur):
            val *= ((duration_sec - t) / fade_dur)
            
        # Normalize and soft clamp
        val = max(-0.95, min(0.95, val * 0.75))
        sample_int = int(val * 32767)
        samples.append(sample_int)
        
    with wave.open(out_path, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        packed = struct.pack(f'<{len(samples)}h', *samples)
        wf.writeframes(packed)
        
    print(f"[+] Ambience soundscape saved to {out_path}")
    return out_path

def process_video(video_path, music_wav):
    fn = Path(video_path).stem
    ext = Path(video_path).suffix
    
    muted_out = OUT_DIR / f"{fn}_muted.mp4"
    music_out = OUT_DIR / f"{fn}_music.mp4"
    
    print(f"\n[*] Processing: {fn}{ext}...")
    
    # 1. Create clean muted version
    cmd_mute = [
        ffmpeg, '-y',
        '-i', str(video_path),
        '-an',  # Strip audio
        '-c:v', 'copy',
        str(muted_out)
    ]
    subprocess.run(cmd_mute, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  [+] Muted Video: {muted_out.name} ({round(muted_out.stat().st_size/1024/1024, 2)} MB)")
    
    # 2. Create music-enhanced version
    cmd_music = [
        ffmpeg, '-y',
        '-i', str(video_path),
        '-stream_loop', '-1',
        '-i', str(music_wav),
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        str(music_out)
    ]
    subprocess.run(cmd_music, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  [+] Music Video: {music_out.name} ({round(music_out.stat().st_size/1024/1024, 2)} MB)")
    
    return str(muted_out), str(music_out)

if __name__ == "__main__":
    wav_path = generate_ambient_tanpura_wav(duration_sec=35)
    
    tg_dir = Path(r"C:\Users\Aksha\Downloads\Telegram Desktop")
    target_videos = [
        "VID-20250804-WA0177.mp4",  # Anshita applying makeup with brush in studio
        "VID-20250807-WA0408.mp4",  # Bengali bride paan leaf reveal ritual
        "VID-20250807-WA0413.mp4",  # Bride with earthen dhunuchi bowl & Banarasi
        "VID-20250804-WA0178.mp4",  # Bengali bride looking into camera with paan
        "VID-20250807-WA0396.mp4",  # Bride profile close-up
    ]
    
    processed = []
    for vid in target_videos:
        p = tg_dir / vid
        if p.exists():
            muted, music = process_video(p, wav_path)
            processed.append({"original": vid, "muted": muted, "music": music})
            
    print(f"\n[✓] Successfully processed {len(processed)} Telegram bridal videos!")
