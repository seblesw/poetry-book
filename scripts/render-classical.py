#!/usr/bin/env python3
"""Soft piano arrangements of public-domain classical pieces."""

from __future__ import annotations

import array
import math
import random
import struct
import subprocess
import wave
from pathlib import Path

SR = 22050
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "audio"
OUT.mkdir(parents=True, exist_ok=True)
random.seed(7)


def freq(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def build_voice(midi: int, seconds: float, decay: float) -> array.array:
    n = int(SR * seconds)
    buf = array.array("f", [0.0]) * n
    f0 = freq(midi)
    partials = (
        (1.0, 1.00, decay),
        (2.0, 0.48, decay * 1.55),
        (3.0, 0.24, decay * 2.15),
        (4.0, 0.12, decay * 2.8),
        (5.0, 0.06, decay * 3.6),
        (6.0, 0.03, decay * 4.4),
    )
    for harm, amp, dec in partials:
        f = f0 * harm * (1.0 + 0.00012 * harm * harm)
        if f >= SR * 0.45:
            continue
        step = 2.0 * math.pi * f / SR
        phase = 0.0
        for i in range(n):
            t = i / SR
            env = math.exp(-dec * t)
            if t < 0.006:
                env *= t / 0.006
            buf[i] += amp * env * math.sin(phase)
            phase += step
            if phase > 6.283185:
                phase -= 6.283185
    peak = max(abs(sample) for sample in buf) or 1.0
    for i in range(n):
        buf[i] /= peak
    return buf


VOICES: dict[tuple[int, float, float], array.array] = {}


def voice(midi: int, seconds: float, decay: float) -> array.array:
    key = (midi, round(seconds, 2), round(decay, 2))
    if key not in VOICES:
        VOICES[key] = build_voice(midi, seconds, decay)
    return VOICES[key]


def mix(events: list[tuple[float, int, float, float, float]], total: float) -> array.array:
    n = int(SR * total)
    buf = array.array("f", [0.0]) * n
    for start, midi, dur, vel, decay in events:
        src = voice(midi, dur + 0.05, decay)
        i0 = int(start * SR)
        length = min(len(src), int(dur * SR), n - i0)
        if length <= 8 or i0 >= n:
            continue
        fade = min(180, length // 3)
        for i in range(length):
            gain = 1.0
            if i > length - fade:
                gain = (length - i) / fade
            buf[i0 + i] += vel * gain * src[i]
    wet = array.array("f", buf)
    delay = int(SR * 0.037)
    for i in range(delay, n):
        wet[i] += 0.22 * wet[i - delay]
    delay2 = int(SR * 0.083)
    for i in range(delay2, n):
        wet[i] += 0.12 * wet[i - delay2]
    peak = 1e-6
    for i in range(n):
        sample = buf[i] * 0.78 + wet[i] * 0.22
        buf[i] = sample
        peak = max(peak, abs(sample))
    scale = 0.72 / peak
    rms = 0.0
    for i in range(n):
        buf[i] *= scale
        rms += buf[i] * buf[i]
    print(f"rms {math.sqrt(rms / n):.4f} peak-before {peak:.3f}")
    return buf


def write_mp3(name: str, buf: array.array) -> None:
    wav_path = OUT / f"{name}.wav"
    mp3_path = OUT / f"{name}.mp3"
    with wave.open(str(wav_path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        frames = bytearray()
        for sample in buf:
            value = max(-1.0, min(1.0, sample))
            frames += struct.pack("<h", int(value * 32767))
        handle.writeframes(frames)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav_path), "-c:a", "libmp3lame", "-q:a", "4", str(mp3_path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    wav_path.unlink()
    print(name, mp3_path.stat().st_size)


def gymnopedie() -> list[tuple[float, int, float, float, float]]:
    beat = 60 / 66
    events: list[tuple[float, int, float, float, float]] = []
    bars = [
        (38, (55, 59, 62), 78),
        (38, (55, 59, 62), 76),
        (38, (54, 57, 61), 74),
        (38, (54, 57, 61), 71),
        (45, (52, 55, 59), 69),
        (45, (52, 55, 59), 74),
        (38, (54, 57, 61), 73),
        (38, (54, 57, 62), 66),
    ]
    for loop in range(2):
        for index, (bass, chord, melody) in enumerate(bars):
            t = (loop * len(bars) + index) * 3 * beat
            events.append((t, bass, beat * 2.6, 0.34, 0.85))
            events.append((t, bass + 12, beat * 2.2, 0.16, 1.1))
            for hit in (1, 2):
                for note in chord:
                    events.append((t + hit * beat, note, beat * 0.92, 0.22, 1.7))
            events.append((t, melody, beat * 2.7, 0.3, 0.7))
    t_end = 16 * 3 * beat
    for note, vel in ((38, 0.36), (50, 0.2), (54, 0.18), (57, 0.16), (62, 0.22)):
        events.append((t_end, note, beat * 4, vel, 0.55))
    return events


def prelude() -> list[tuple[float, int, float, float, float]]:
    step = 60 / 76 / 4
    shapes = [
        (60, 64, 67, 72, 76),
        (60, 62, 69, 74, 77),
        (59, 62, 67, 74, 77),
        (60, 64, 67, 72, 76),
        (60, 64, 69, 76, 81),
        (60, 62, 66, 69, 74),
        (59, 62, 67, 74, 79),
        (59, 60, 64, 67, 72),
        (57, 60, 64, 67, 72),
        (55, 62, 67, 71, 74),
        (55, 59, 62, 67, 71),
        (55, 60, 64, 67, 72),
    ]
    events: list[tuple[float, int, float, float, float]] = []
    for bar, shape in enumerate(shapes):
        group = (shape[0], shape[1], shape[2], shape[3], shape[4], shape[2], shape[3], shape[4])
        for half in range(2):
            for index, note in enumerate(group):
                t = (bar * 16 + half * 8 + index) * step
                events.append((t, note, step * 3.2, 0.28, 3.4))
    t_end = len(shapes) * 16 * step
    for note, vel in ((48, 0.34), (60, 0.24), (64, 0.2), (67, 0.18), (72, 0.16)):
        events.append((t_end, note, 2.4, vel, 0.7))
    return events


def moonlight() -> list[tuple[float, int, float, float, float]]:
    quarter = 60 / 50
    trip = quarter / 3
    events: list[tuple[float, int, float, float, float]] = []
    basses = [37, 37, 35, 35, 33, 42, 44, 37]
    triplets = [
        (56, 61, 64),
        (56, 61, 64),
        (56, 61, 64),
        (56, 61, 64),
        (57, 61, 64),
        (56, 61, 64),
        (56, 61, 66),
        (56, 61, 64),
    ]
    melody = [None, None, None, None, 68, 73, 76, 73]
    for bar in range(8):
        t = bar * 4 * quarter
        events.append((t, basses[bar], quarter * 3.6, 0.4, 0.65))
        events.append((t, basses[bar] + 12, quarter * 3.2, 0.22, 0.8))
        chord = triplets[bar]
        for beat in range(12):
            note = chord[beat % 3]
            events.append((t + beat * trip, note, trip * 2.4, 0.16, 2.8))
        if melody[bar] is not None:
            events.append((t, melody[bar], quarter * 3.2, 0.26, 0.75))
    t_end = 8 * 4 * quarter
    for note, vel in ((37, 0.38), (49, 0.2), (56, 0.16), (61, 0.14), (64, 0.16)):
        events.append((t_end, note, 3.2, vel, 0.55))
    return events


def main() -> None:
    pieces = {
        "gymnopedie": (gymnopedie(), 16 * 3 * (60 / 66) + 4.2),
        "prelude": (prelude(), 12 * 16 * (60 / 76 / 4) + 3.2),
        "moonlight": (moonlight(), 8 * 4 * (60 / 50) + 3.6),
    }
    for name, (events, total) in pieces.items():
        print("render", name)
        write_mp3(name, mix(events, total))


if __name__ == "__main__":
    main()
