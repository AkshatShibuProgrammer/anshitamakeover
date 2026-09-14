import os
import json
import miniaudio
import numpy as np

def analyze_track(mp3_path, track_name):
    print(f"[*] Analyzing waveform & acoustic energy for: {track_name} ...")
    decoded = miniaudio.decode_file(mp3_path, output_format=miniaudio.SampleFormat.SIGNED16)
    sr = decoded.sample_rate
    channels = decoded.nchannels
    
    # Convert samples to numpy float array
    samples = np.frombuffer(decoded.samples, dtype=np.int16).astype(np.float32) / 32768.0
    if channels == 2:
        samples = (samples[0::2] + samples[1::2]) / 2.0  # Mix down to mono for onset/energy analysis

    duration = len(samples) / float(sr)
    
    # Analyze in 100ms energy windows (0.1s resolution)
    window_size = int(sr * 0.1)
    hop_size = int(sr * 0.05) # 50ms hop
    
    times = []
    energies = []
    spectral_flux = []
    prev_spectrum = None
    
    for start in range(0, len(samples) - window_size, hop_size):
        chunk = samples[start:start + window_size]
        t = start / float(sr)
        rms = np.sqrt(np.mean(chunk**2))
        times.append(t)
        energies.append(rms)
        
        # Simple FFT flux for beat/break attack detection
        spectrum = np.abs(np.fft.rfft(chunk * np.hanning(len(chunk))))
        if prev_spectrum is not None and len(prev_spectrum) == len(spectrum):
            flux = np.sum(np.maximum(0, spectrum - prev_spectrum))
            spectral_flux.append(flux)
        else:
            spectral_flux.append(0.0)
        prev_spectrum = spectrum
        
    times = np.array(times)
    energies = np.array(energies)
    spectral_flux = np.array(spectral_flux)
    
    # Find natural musical phrasing breakpoints (phrase transitions, breath pauses, drop attacks)
    # Breakpoints are local minima in RMS followed by sharp rises in flux
    breakpoints = []
    
    # Always include track start as breakpoint 0
    breakpoints.append({
        "time": 0.0,
        "type": "intro",
        "description": "Opening Prelude",
        "energy": float(energies[0])
    })
    
    for i in range(10, len(energies) - 20):
        t = times[i]
        # Check for phrase boundaries: pause/dip followed by rise
        local_min = energies[i] < energies[i-4] and energies[i] < energies[i+4]
        rise = energies[i+6] > energies[i] * 1.35 or spectral_flux[i+2] > np.mean(spectral_flux) * 1.5
        
        if (local_min and rise) or (spectral_flux[i] > np.percentile(spectral_flux, 92)):
            # Enforce at least 3.5 seconds separation between distinct cut breakpoints
            if not breakpoints or (t - breakpoints[-1]["time"]) >= 3.5:
                bp_type = "crescendo" if rise else "phrase_start"
                breakpoints.append({
                    "time": round(float(t), 2),
                    "type": bp_type,
                    "description": f"Musical Phrasing Drop @ {int(t//60)}m {int(t%60)}s",
                    "energy": round(float(energies[i]), 3)
                })
                
    print(f"[+] Found {len(breakpoints)} distinct musical breakpoints in {track_name}")
    return {
        "track_name": track_name,
        "file": mp3_path,
        "duration": round(duration, 2),
        "sample_rate": sr,
        "channels": channels,
        "breakpoints": breakpoints
    }

def cut_music_clip(mp3_path, start_time, duration, output_path):
    """Accurately slices audio with gentle 0.5s fade-in and 0.8s fade-out."""
    decoded = miniaudio.decode_file(mp3_path, output_format=miniaudio.SampleFormat.SIGNED16)
    sr = decoded.sample_rate
    channels = decoded.nchannels
    
    samples = np.frombuffer(decoded.samples, dtype=np.int16).copy()
    
    start_frame = int(start_time * sr) * channels
    end_frame = int((start_time + duration) * sr) * channels
    
    # If duration extends past end, loop or truncate
    if end_frame > len(samples):
        sliced = samples[start_frame:]
    else:
        sliced = samples[start_frame:end_frame]
        
    sliced_float = sliced.astype(np.float32)
    
    # Apply fade in
    fade_in_samples = int(sr * 0.4) * channels
    if len(sliced_float) > fade_in_samples:
        fade_curve = np.linspace(0.0, 1.0, fade_in_samples // channels)
        fade_curve = np.repeat(fade_curve, channels)
        sliced_float[:len(fade_curve)] *= fade_curve
        
    # Apply fade out
    fade_out_samples = int(sr * 0.7) * channels
    if len(sliced_float) > fade_out_samples:
        fade_curve = np.linspace(1.0, 0.0, fade_out_samples // channels)
        fade_curve = np.repeat(fade_curve, channels)
        sliced_float[-len(fade_curve):] *= fade_curve
        
    final_pcm = np.clip(sliced_float, -32768, 32767).astype(np.int16)
    
    # Save as high quality WAV
    import wave
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(final_pcm.tobytes())
        
    print(f"[+] Exported sliced music: {output_path} (Start: {start_time}s, Length: {duration}s)")

if __name__ == "__main__":
    t1 = analyze_track("music/Morning_at_the_Palace.mp3", "Morning at the Palace")
    t2 = analyze_track("music/The_Saffron_Veil.mp3", "The Saffron Veil")
    
    os.makedirs("temp/music_analysis", exist_ok=True)
    with open("temp/music_analysis/breakpoints.json", "w") as f:
        json.dump([t1, t2], f, indent=2)
        
    print("\n[*] Exporting sample cuts for reel lengths (8s and 14s)...")
    # Cut sample 1: Morning at the Palace from 2nd breakpoint (8 sec reel)
    bp1 = t1["breakpoints"][1]["time"]
    cut_music_clip("music/Morning_at_the_Palace.mp3", bp1, 8.0, "temp/music_analysis/morning_palace_reel8s.wav")
    
    # Cut sample 2: The Saffron Veil from 3rd breakpoint (14 sec reel)
    bp2 = t2["breakpoints"][2]["time"]
    cut_music_clip("music/The_Saffron_Veil.mp3", bp2, 14.0, "temp/music_analysis/saffron_veil_reel14s.wav")
    
    print("\n[✓] Breakpoint analysis & cutting suite ready!")
