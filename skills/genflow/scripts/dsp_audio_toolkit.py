"""
DSP Audio Toolkit: State-of-the-Art Algorithmic Audio Synthesizer for /genflow
- 7-Voice Stereo Supersaw (JP-8000 Model with PolyBLEP Anti-Aliasing)
- Moog 24dB/octave Resonant Ladder Filter (Hammerstein Saturation)
- Schroeder-Moorer Algorithmic Reverberator (Block-Vectorized via SciPy)
- Vectorized Drum Generators (Kick, Snare, Hi-Hat)
- Timeline SSOT Synthesizer & Multi-track Mixer
"""

import math
import struct
import wave
import os
import sys
import json
import argparse
import numpy as np
from scipy.signal import lfilter

SAMPLE_RATE = 44100

# --- 1. DRUM GENERATORS (VECTORIZED) ---

def generate_kick(duration=0.28, start_freq=180.0, end_freq=42.0, sample_rate=SAMPLE_RATE):
    """Kick Drum with Exponential Pitch Drop and Soft-Clipping Saturation"""
    n = int(duration * sample_rate)
    t = np.linspace(0, duration, n, endpoint=False)
    freq = (start_freq - end_freq) * np.exp(-30.0 * t) + end_freq
    phase = 2.0 * np.pi * np.cumsum(freq) / sample_rate
    amp = np.exp(-12.0 * t)
    kick = np.tanh(np.sin(phase) * 1.8) * amp * 0.95
    return np.stack([kick, kick], axis=1)

def generate_snare(duration=0.22, sample_rate=SAMPLE_RATE):
    """Snare Drum with Sine Body Punch and Filtered White Noise"""
    n = int(duration * sample_rate)
    t = np.linspace(0, duration, n, endpoint=False)
    tone = np.sin(2.0 * np.pi * 185.0 * t) * np.exp(-35.0 * t) * 0.5
    noise = np.random.uniform(-1.0, 1.0, n) * np.exp(-16.0 * t) * 0.6
    snare = np.tanh((tone + noise) * 1.4) * 0.85
    return np.stack([snare, snare], axis=1)

def generate_hihat(duration=0.06, sample_rate=SAMPLE_RATE):
    """Hi-Hat with Ultra-Short White Noise Exponential Decay"""
    n = int(duration * sample_rate)
    t = np.linspace(0, duration, n, endpoint=False)
    noise = np.random.uniform(-1.0, 1.0, n) * np.exp(-65.0 * t) * 0.4
    return np.stack([noise * 0.8, noise * 1.2], axis=1)

# --- 2. 7-VOICE STEREO SUPERSAW (JP-8000 POLYBLEP) ---

OFFS = np.array([-0.11002313, -0.06288439, -0.01952356, 0.0,
                  0.01991221,  0.06216538,  0.10745242])
_DC = [10028.7312891634, -50818.8652045924, 111363.4808729368, -138150.6761080548,
       106649.6679158292, -53046.9642751875, 17019.9518580080, -3425.0836591318,
       404.2703938388, -24.1878824391, 0.6717417634, 0.0030115596]
detune_curve = lambda x: np.polyval(_DC, x)

def polyblep(t, dt):
    """Residual Polynomial Band-Limited Step for Anti-Aliasing"""
    safe_dt = np.where(dt <= 1e-9, 1.0, dt)
    x = t / safe_dt
    y = np.where((dt > 1e-9) & (t < dt), 2.0 * x - x * x - 1.0, 0.0)
    x = (t - 1.0) / safe_dt
    return np.where((dt > 1e-9) & (t > 1.0 - dt), x * x + 2.0 * x + 1.0, y)

def supersaw(f, fs=SAMPLE_RATE, detune=0.5, mix=0.5, width=0.8, seed=0):
    """
    7-Voice Stereo Supersaw based on Roland JP-8000 Model
    f: note frequency (scalar or 1D array of length n)
    returns: stereo array (n, 2)
    """
    if np.isscalar(f):
        f = np.full(int(0.25 * fs), f)
    n = len(f)
    rng = np.random.default_rng(seed)
    cv = -0.55366 * mix + 0.99785
    sv = -0.73764 * mix**2 + 1.2841 * mix + 0.044372
    gains = np.where(OFFS == 0, cv, sv)
    pan = np.array([-1, -.66, -.33, 0, .33, .66, 1.0]) * width
    dt = f[None, :] * (1.0 + OFFS[:, None] * detune_curve(detune)) / fs
    ph = (np.cumsum(dt, axis=1) + rng.random((7, 1))) % 1.0
    saw = 2.0 * ph - 1.0 - polyblep(ph, dt)
    ang = (pan + 1.0) * np.pi / 4.0
    L = (gains * np.cos(ang)) @ saw
    R = (gains * np.sin(ang)) @ saw
    out = np.stack([L, R], axis=1)
    return out / np.sqrt((gains**2).sum())

# --- 3. MOOG 24dB/OCTAVE RESONANT FILTER ---

def ladder_linear(x, fc, k, fs=SAMPLE_RATE, blk=32):
    """Moog 4-pole linear filter block-updated for smooth cutoff sweeps"""
    y = np.empty_like(x)
    zi = np.zeros(4)
    p = lambda a: np.array([1.0, -(1.0 - a)])
    n = len(x)
    for i in range(0, n, blk):
        raw_fc = fc[i] if hasattr(fc, '__len__') else fc
        cur_fc = min(max(float(raw_fc), 20.0), fs * 0.45)
        a = 1.0 - np.exp(-2.0 * np.pi * cur_fc / fs)
        den = np.array([1.0])
        for _ in range(4):
            den = np.convolve(den, p(a))
        den[0] += k * (a**4)
        end_idx = min(i + blk, n)
        y[i:end_idx], zi = lfilter([a**4], den, x[i:end_idx], zi=zi)
    return y

def moog_fast(x, fc, k=2.5, fs=SAMPLE_RATE, drive=2.0):
    """Hammerstein Sandwich Moog Filter (Tanh Saturation pre & post ladder)"""
    if x.ndim == 2:
        return np.stack([
            np.tanh(1.5 * ladder_linear(np.tanh(drive * x[:, 0]), fc, min(k, 3.8), fs)),
            np.tanh(1.5 * ladder_linear(np.tanh(drive * x[:, 1]), fc, min(k, 3.8), fs))
        ], axis=1)
    return np.tanh(1.5 * ladder_linear(np.tanh(drive * x), fc, min(k, 3.8), fs))

# --- 4. SCHROEDER-MOORER REVERB (BLOCK-VECTORIZED) ---

def _pad(x, D):
    n = -(-len(x) // D) * D
    xp = np.zeros(n)
    xp[:len(x)] = x
    return xp, n

def comb(x, D, g, d=0.25):
    xp, n = _pad(x, D)
    y = np.zeros(n)
    prev = np.zeros(D)
    zi = np.zeros(1)
    for k in range(0, n, D):
        blk = xp[k:k+D] + g * prev
        y[k:k+D] = blk
        prev, zi = lfilter([1.0 - d], [1.0, -d], blk, zi=zi)
    return y[:len(x)]

def allpass(x, D, g=0.5):
    xp, n = _pad(x, D)
    y = np.zeros(n)
    xprev = np.zeros(D)
    yprev = np.zeros(D)
    for k in range(0, n, D):
        xb = xp[k:k+D]
        yb = -g * xb + xprev + g * yprev
        y[k:k+D] = yb
        xprev, yprev = xb, yb
    return y[:len(x)]

def schroeder_moorer(x, fs=SAMPLE_RATE, rt60=2.0, damp=0.25, mix=0.3, spread=23):
    """4 Parallel Comb Filters + 2 Series All-Pass Filters with Stereo Decorrelation"""
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    out = []
    for ch, off in ((0, 0), (1, spread)):
        w = sum(comb(x[:, ch], D + off, 10**(-3.0 * (D + off) / (fs * rt60)), damp)
                for D in (1116, 1188, 1277, 1356)) / 4.0
        for D in (556, 441):
            w = allpass(w, D + off, 0.5)
        out.append(w)
    wet = np.stack(out, axis=1)
    return (1.0 - mix) * x + mix * wet

# --- 5. EXPORT & MASTERING ---

def export_wav(audio_stereo, output_path, sample_rate=SAMPLE_RATE):
    """Normalize and export to 16-bit Stereo PCM WAV"""
    audio_stereo = np.asarray(audio_stereo)
    if audio_stereo.ndim == 1:
        audio_stereo = np.stack([audio_stereo, audio_stereo], axis=1)
    elif audio_stereo.ndim > 2:
        raise ValueError("Audio data must be 1D (mono) or 2D (stereo).")
    max_peak = np.max(np.abs(audio_stereo)) + 1e-6
    norm = np.clip(audio_stereo / max_peak, -0.98, 0.98)
    int_samples = (norm * 32767.0).astype(np.int16)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int_samples.tobytes())
    return output_path

# --- 6. DEMO & TIMELINE SYNTHESIS ---

def generate_demo_showreel(duration=4.0, bpm=128, output_path="nextgen_demo_beat.wav"):
    """Synthesize high-energy showreel demonstrating Supersaw + Moog Sweep + Reverb"""
    total_samples = int(duration * SAMPLE_RATE)
    mix = np.zeros((total_samples, 2), dtype=np.float32)
    beat_dur = 60.0 / bpm
    
    # 1. Kick on quarter notes
    kick = generate_kick(duration=0.28)
    for b in range(int(duration / beat_dur)):
        start = int(b * beat_dur * SAMPLE_RATE)
        k_len = min(len(kick), total_samples - start)
        mix[start:start+k_len] += kick[:k_len]
        
    # 2. Snare on beats 1 and 3
    snare = generate_snare(duration=0.22)
    for b in range(1, int(duration / beat_dur), 2):
        start = int(b * beat_dur * SAMPLE_RATE)
        s_len = min(len(snare), total_samples - start)
        mix[start:start+s_len] += snare[:s_len]
        
    # 3. Supersaw Lead Arpeggio with Moog Sweep
    notes = [220.0, 261.63, 329.63, 392.0, 440.0, 329.63, 261.63, 196.0]
    step_dur = beat_dur / 4.0
    synth_bus = np.zeros((total_samples, 2), dtype=np.float32)
    
    for i, t_start in enumerate(np.arange(0, duration, step_dur)):
        idx = int(t_start * SAMPLE_RATE)
        step_len = int(step_dur * SAMPLE_RATE)
        if idx + step_len > total_samples: break
        
        freq = notes[i % len(notes)]
        f_arr = np.full(step_len, freq)
        saw_voice = supersaw(f_arr, detune=0.6, mix=0.7, width=0.9, seed=i)
        
        t_env = np.linspace(0, step_dur, step_len, endpoint=False)
        env = np.exp(-12.0 * t_env)[:, None]
        synth_bus[idx:idx+step_len] += saw_voice * env * 0.45
        
    fc_sweep = np.linspace(600.0, 6500.0, total_samples)
    filtered_synth = moog_fast(synth_bus, fc=fc_sweep, k=2.8)
    reverbed_synth = schroeder_moorer(filtered_synth, rt60=2.2, mix=0.35)
    mix += reverbed_synth
    
    return export_wav(mix, output_path)

def synthesize_from_timeline(timeline_path, output_path):
    """Synthesize complete soundtrack compiled from timeline.json contract"""
    with open(timeline_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    bpm = meta.get("bpm", 120.0)
    duration = meta.get("duration", 15.0)
    total_samples = int(duration * SAMPLE_RATE)
    mix = np.zeros((total_samples, 2), dtype=np.float32)
    beat_dur = 60.0 / bpm
    
    # Render rhythm events
    kick = generate_kick(duration=0.28)
    snare = generate_snare(duration=0.22)
    hihat = generate_hihat(duration=0.06)
    
    for b in range(int(duration / beat_dur)):
        t_sec = b * beat_dur
        idx = int(t_sec * SAMPLE_RATE)
        # Kick on 0 and 2
        if b % 2 == 0 and idx < total_samples:
            kl = min(len(kick), total_samples - idx)
            mix[idx:idx+kl] += kick[:kl]
        # Snare on 1 and 3
        if b % 2 == 1 and idx < total_samples:
            sl = min(len(snare), total_samples - idx)
            mix[idx:idx+sl] += snare[:sl]
        # Hihat on 8th notes
        for off in [0.0, beat_dur / 2.0]:
            h_idx = int((t_sec + off) * SAMPLE_RATE)
            if h_idx < total_samples:
                hl = min(len(hihat), total_samples - h_idx)
                mix[h_idx:h_idx+hl] += hihat[:hl] * 0.45

    # Render events or chords from manifest if present
    events = meta.get("audio_events", [])
    synth_bus = np.zeros((total_samples, 2), dtype=np.float32)
    
    # If audio_events not explicitly provided, generate rich harmonic chords from scenes
    if not events and meta.get("scenes"):
        scene_chords = [220.0, 261.63, 329.63, 392.0, 440.0, 349.23, 293.66]
        for s_i, sc in enumerate(meta.get("scenes", [])):
            s_t = float(sc.get("start", s_i * 3.0))
            e_t = float(sc.get("end", s_t + 3.0))
            dur = max(0.5, e_t - s_t)
            freq = scene_chords[s_i % len(scene_chords)]
            events.append({"time": s_t, "duration": dur, "freq": freq})

    for ev in events:
        start_t = ev.get("time", 0.0)
        dur = ev.get("duration", 1.0)
        freq = ev.get("freq", 220.0)
        start_idx = int(start_t * SAMPLE_RATE)
        num_s = int(dur * SAMPLE_RATE)
        if start_idx + num_s > total_samples:
            num_s = total_samples - start_idx
        if num_s <= 0: continue
        
        f_arr = np.full(num_s, freq)
        voice = supersaw(f_arr, detune=0.5, mix=0.6, width=0.8)
        t_env = np.linspace(0, dur, num_s, endpoint=False)
        env = np.exp(-4.0 * t_env)[:, None]
        synth_bus[start_idx:start_idx+num_s] += voice * env * 0.5
        
    if np.any(synth_bus):
        fc_mod = np.linspace(800.0, 4800.0, total_samples)
        filtered = moog_fast(synth_bus, fc=fc_mod, k=2.0)
        rev = schroeder_moorer(filtered, rt60=2.5, mix=0.3)
        mix += rev

    return export_wav(mix, output_path)

def generate_supersaw_moog_track(bars=4, bpm=128.0, output_path="lead_moog_bass.wav"):
    """
    Synthesize complete multi-bar pure math track:
    - Punchy Kick, Snare, 16th Hi-Hats
    - 24dB Moog Ladder Resonant Bassline (Saw + Sub-Sine, cutoff envelope, sidechain ducking)
    - 7-Voice PolyBLEP Stereo Supersaw Lead Arpeggio + Schroeder Reverb
    """
    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4.0
    duration = bar_dur * bars
    total_samples = int(duration * SAMPLE_RATE)
    mix = np.zeros((total_samples, 2), dtype=np.float32)

    # 1. Drums
    total_beats = bars * 4
    kick = generate_kick(duration=0.28)
    for b in range(total_beats):
        idx = int(b * beat_dur * SAMPLE_RATE)
        kl = min(len(kick), total_samples - idx)
        mix[idx:idx+kl] += kick[:kl] * 0.90

    snare = generate_snare(duration=0.22)
    for b in range(1, total_beats, 2):
        idx = int(b * beat_dur * SAMPLE_RATE)
        sl = min(len(snare), total_samples - idx)
        mix[idx:idx+sl] += snare[:sl] * 0.80

    hat = generate_hihat(duration=0.05)
    step_dur = beat_dur / 4.0
    for s in range(total_beats * 4):
        idx = int(s * step_dur * SAMPLE_RATE)
        hl = min(len(hat), total_samples - idx)
        vel = 0.40 if s % 4 == 2 else 0.22
        mix[idx:idx+hl] += hat[:hl] * vel

    # 2. Moog Bassline (Continuous sample-accurate boundaries)
    bar_bass_notes = [
        [36.71, 73.42, 36.71, 73.42, 36.71, 36.71, 73.42, 36.71, 36.71, 73.42, 36.71, 73.42, 36.71, 36.71, 73.42, 55.00],
        [43.65, 87.31, 43.65, 87.31, 43.65, 43.65, 87.31, 43.65, 43.65, 87.31, 43.65, 87.31, 43.65, 43.65, 87.31, 65.41],
        [48.99, 97.99, 48.99, 97.99, 48.99, 48.99, 97.99, 48.99, 48.99, 97.99, 48.99, 97.99, 48.99, 48.99, 97.99, 73.42],
        [58.27, 58.27, 58.27, 58.27, 65.41, 65.41, 65.41, 65.41, 55.00, 55.00, 55.00, 55.00, 73.42, 73.42, 36.71, 36.71]
    ]
    raw_bass = np.zeros((total_samples, 2), dtype=np.float32)
    fc_bass = np.full(total_samples, 250.0, dtype=np.float32)

    for s_idx in range(total_beats * 4):
        idx = int(s_idx * step_dur * SAMPLE_RATE)
        idx_next = min(int((s_idx + 1) * step_dur * SAMPLE_RATE), total_samples)
        cur_samples = idx_next - idx
        if cur_samples <= 0 or idx >= total_samples:
            break
        stept = np.linspace(0, cur_samples / SAMPLE_RATE, cur_samples, endpoint=False)
        amp_env = np.exp(-14.0 * stept)[:, None]
        
        # Loop progression if bars > 4
        bar_idx = int((s_idx * step_dur) / bar_dur) % len(bar_bass_notes)
        freq = bar_bass_notes[bar_idx][s_idx % 16]
        f_arr = np.full(cur_samples, freq)
        saw_voice = supersaw(f_arr, detune=0.35, mix=0.5, width=0.4, seed=s_idx + 100)
        sub_sine = np.sin(2.0 * np.pi * freq * stept)[:, None] * 0.75
        ducking = 0.35 if (s_idx % 4 == 0) else 0.85
        raw_bass[idx:idx_next] += (saw_voice * 0.8 + sub_sine) * amp_env * ducking
        fc_bass[idx:idx_next] = 220.0 + 2600.0 * np.exp(-24.0 * stept)

    filtered_bass = moog_fast(raw_bass, fc=fc_bass, k=2.7, drive=2.2)
    mix += filtered_bass * 0.85

    # 3. Supersaw Lead Arpeggio
    lead_bus = np.zeros((total_samples, 2), dtype=np.float32)
    lead_patterns = [
        [293.66, 349.23, 440.00, 587.33, 523.25, 440.00, 349.23, 392.00] * 2,
        [349.23, 440.00, 523.25, 698.46, 659.25, 523.25, 440.00, 523.25] * 2,
        [392.00, 466.16, 587.33, 783.99, 698.46, 587.33, 466.16, 587.33] * 2,
        [466.16, 587.33, 698.46, 932.33, 880.00, 698.46, 659.25, 587.33,
         440.00, 554.37, 659.25, 880.00, 783.99, 659.25, 554.37, 440.00]
    ]
    for s_idx in range(total_beats * 4):
        idx = int(s_idx * step_dur * SAMPLE_RATE)
        idx_next = min(int((s_idx + 1) * step_dur * SAMPLE_RATE), total_samples)
        cur_samples = idx_next - idx
        if cur_samples <= 0 or idx >= total_samples:
            break
        stept = np.linspace(0, cur_samples / SAMPLE_RATE, cur_samples, endpoint=False)
        env_lead = np.exp(-8.0 * stept)[:, None]
        
        # Loop lead patterns if bars > 4
        bar_idx = int((s_idx * step_dur) / bar_dur) % len(lead_patterns)
        freq = lead_patterns[bar_idx][s_idx % 16]
        f_arr = np.full(cur_samples, freq)
        voice = supersaw(f_arr, detune=0.55, mix=0.72, width=0.88, seed=s_idx)
        lead_bus[idx:idx_next] += voice * env_lead * 0.40

    fc_lead = np.linspace(1200.0, 6800.0, total_samples)
    lead_filtered = moog_fast(lead_bus, fc=fc_lead, k=2.0, drive=1.5)
    lead_rev = schroeder_moorer(lead_filtered, rt60=2.4, mix=0.35)
    mix += lead_rev * 0.70

    return export_wav(mix, output_path, sample_rate=SAMPLE_RATE)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DSP Audio Toolkit for /genflow")
    parser.add_argument("--demo", action="store_true", help="Generate 4s showreel demo")
    parser.add_argument("--lead-bass", action="store_true", help="Generate Supersaw Lead + Moog Filter Bassline track")
    parser.add_argument("--bars", type=int, default=4, help="Number of bars for --lead-bass (default: 4)")
    parser.add_argument("--duration", type=float, default=4.0, help="Duration in seconds")
    parser.add_argument("--bpm", type=float, default=128.0, help="Tempo in BPM")
    parser.add_argument("--timeline", type=str, help="Path to timeline.json")
    parser.add_argument("--out", type=str, default="output_audio.wav", help="Output WAV path")
    args = parser.parse_args()
    
    if args.lead_bass:
        print(f"Synthesizing Supersaw Lead + Moog Bassline ({args.bars} bars @ {args.bpm} BPM) -> {args.out}...")
        res = generate_supersaw_moog_track(bars=args.bars, bpm=args.bpm, output_path=args.out)
        print(f"Done! Created: {res} ({os.path.getsize(res)} bytes)")
    elif args.timeline:
        print(f"Synthesizing soundtrack from timeline {args.timeline} -> {args.out}...")
        res = synthesize_from_timeline(args.timeline, args.out)
        print(f"Done! Created: {res} ({os.path.getsize(res)} bytes)")
    elif args.demo:
        print(f"Synthesizing Demo Beat ({args.duration}s @ {args.bpm} BPM) -> {args.out}...")
        res = generate_demo_showreel(duration=args.duration, bpm=args.bpm, output_path=args.out)
        print(f"Done! Created: {res} ({os.path.getsize(res)} bytes)")
    else:
        parser.print_help()
