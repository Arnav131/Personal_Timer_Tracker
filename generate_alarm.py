"""
Generate a soft, gentle chime alarm tone as alarm.mp3.
Uses numpy and scipy to create a bell-like sine wave tone.
Run this script once to create the assets/alarm.mp3 file.
"""

import struct
import wave
import math
import os
import subprocess
import sys


def generate_chime_wav(output_path, duration=2.5, sample_rate=44100):
    """Generate a gentle bell chime as a WAV file."""
    num_samples = int(sample_rate * duration)
    samples = []

    # Bell frequencies — harmonically related for a pleasant chime
    harmonics = [
        (523.25, 1.0),    # C5 — fundamental
        (659.25, 0.6),    # E5 — major third
        (783.99, 0.4),    # G5 — fifth
        (1046.50, 0.25),  # C6 — octave
        (1318.51, 0.15),  # E6 — high third
    ]

    for i in range(num_samples):
        t = i / sample_rate
        sample = 0.0

        for freq, amplitude in harmonics:
            # Exponential decay envelope for bell-like quality
            decay = math.exp(-t * 2.0)
            # Slight frequency modulation for richness
            vibrato = 1.0 + 0.002 * math.sin(2 * math.pi * 5.5 * t)
            sample += amplitude * decay * math.sin(2 * math.pi * freq * vibrato * t)

        # Smooth fade-in over first 50ms to avoid clicks
        if t < 0.05:
            sample *= t / 0.05

        # Smooth fade-out over last 200ms
        time_left = duration - t
        if time_left < 0.2:
            sample *= time_left / 0.2

        # Normalize to 16-bit range
        sample = max(-1.0, min(1.0, sample * 0.3))
        samples.append(int(sample * 32767))

    # Create the complete audio: three chimes with gaps
    full_samples = []
    gap_samples = [0] * int(sample_rate * 0.4)  # 400ms gap

    for chime_idx in range(3):
        # Each subsequent chime slightly quieter
        volume = 1.0 - (chime_idx * 0.15)
        for s in samples:
            full_samples.append(int(s * volume))
        if chime_idx < 2:
            full_samples.extend(gap_samples)

    # Write WAV file
    wav_path = output_path.replace('.mp3', '.wav')
    with wave.open(wav_path, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in full_samples:
            wav_file.writeframes(struct.pack('<h', sample))

    return wav_path


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    output = os.path.join(assets_dir, "alarm.mp3")
    wav_path = generate_chime_wav(output)

    # Try to convert to MP3 using ffmpeg if available
    mp3_path = output
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path],
            capture_output=True, check=True
        )
        os.remove(wav_path)
        print(f"Generated MP3: {mp3_path}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # ffmpeg not available — keep WAV and rename
        # pygame can play WAV files just fine
        final_path = wav_path  # Keep as .wav
        print(f"ffmpeg not found. Generated WAV: {wav_path}")
        print("Pygame can play WAV files — the app will work fine.")
