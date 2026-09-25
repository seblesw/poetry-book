#!/usr/bin/env python3
"""Original pieces in Ethiopian qenet for reading: tizita, bati, ambassel.

Krar is a plucked string. Masenqo is a slow bowed line. Washint is a flute.
These are new arrangements, not recordings of another musician.
"""

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
random.seed(4)

TIZITA = [62, 64, 66, 69, 71]
BATI = [62, 65, 67, 69, 72]
AMBASSEL = [62, 63, 67, 69, 70]


def freq(midi: float) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def pluck(midi: int, seconds: float, bright: float = 0.55) -> array.array:
    f = freq(midi)
    period = max(2, int(SR / f))
    rnd = random.Random(midi * 17 + int(seconds * 10))
    comb = [rnd.uniform(-1, 1) for _ in range(period)]
    # soften the noise so the lyre is round, not metallic
    for _ in range(2):
        comb = [(comb[i] + comb[(i + 1) % period]) * 0.5 for i in range(period)]
    n = int(SR * seconds)
    out = array.array("f", [0.0]) * n
    damp = 0.9965 if midi < 60 else 0.994
    index = 0
    for i in range(n):
        sample = comb[index]
        nxt = (comb[index] * bright + comb[(index + 1) % period] * (1 - bright)) * damp
        comb[index] = nxt
        out[i] = sample * math.exp(-1.15 * i / SR)
        index = (index + 1) % period
    return out


def bow(midi: float, seconds: float, vib: float = 4.5) -> array.array:
    n = int(SR * seconds)
    out = array.array("f", [0.0]) * n
    for i in range(n):
        t = i / SR
        slide = 1 - math.exp(-t * 6)
        f = freq(midi) * (0.985 + 0.015 * slide)
        f *= 1 + 0.008 * math.sin(math.tau * vib * t)
        env = min(1.0, t / 0.08) * math.exp(-0.35 * max(0, t - seconds + 0.4))
        if t > seconds - 0.25:
            env *= max(0, (seconds - t) / 0.25)
        phase = math.tau * f * t
        sample = 0.62 * math.sin(phase) + 0.22 * math.sin(2 * phase) + 0.08 * math.sin(3 * phase)
        breath = 0.04 * math.sin(phase * 1.01 + 0.4)
        out[i] = (sample + breath) * env
    return out


def flute(midi: float, seconds: float) -> array.array:
    n = int(SR * seconds)
    out = array.array("f", [0.0]) * n
    rnd = random.Random(int(midi * 10))
    for i in range(n):
        t = i / SR
        f = freq(midi) * (1 + 0.006 * math.sin(math.tau * 5.2 * t))
        env = min(1.0, t / 0.05)
        if t > seconds - 0.18:
            env *= max(0, (seconds - t) / 0.18)
        phase = math.tau * f * t
        air = 0.07 * (rnd.random() * 2 - 1) * math.exp(-8 * t)
        out[i] = (0.7 * math.sin(phase) + 0.18 * math.sin(2 * phase) + air) * env
    return out


def mix(events: list[tuple], total: float) -> array.array:
    n = int(SR * total)
    buf = array.array("f", [0.0]) * n
    cache: dict[tuple, array.array] = {}
    for start, kind, midi, dur, vel in events:
        key = (kind, round(float(midi), 2), round(dur, 2))
        if key not in cache:
            if kind == "krar":
                cache[key] = pluck(int(midi), dur)
            elif kind == "masenqo":
                cache[key] = bow(float(midi), dur)
            else:
                cache[key] = flute(float(midi), dur)
        src = cache[key]
        i0 = int(start * SR)
        length = min(len(src), n - i0)
        for i in range(length):
            buf[i0 + i] += vel * src[i]
    # a small room, not a cathedral
    delay = int(SR * 0.031)
    for i in range(delay, n):
        buf[i] += 0.18 * buf[i - delay]
    peak = max(abs(sample) for sample in buf) or 1
    scale = 0.78 / peak
    for i in range(n):
        buf[i] *= scale
    return buf


def add_krar_bed(events, scale, beat, bars, root):
    pattern = [scale[0] - 12, scale[2] - 12, scale[4] - 12, scale[1], scale[3]]
    for bar in range(bars):
        for step, note in enumerate(pattern):
            events.append((bar * 4 * beat + step * beat * 0.8, "krar", note, beat * 2.4, 0.34 if step == 0 else 0.22))
        events.append((bar * 4 * beat, "krar", root - 12, beat * 3.5, 0.28))


def tizita() -> tuple[list, float]:
    beat = 60 / 72
    events = []
    add_krar_bed(events, TIZITA, beat, 10, 62)
    melody = [71, 69, 66, 64, 62, 64, 66, 69, 71, 69, 66, 62, 64, 66, 69, 71]
    for i, note in enumerate(melody):
        events.append((i * beat * 2.1 + beat, "washint", note, beat * 1.9, 0.26))
    total = 10 * 4 * beat + 1.2
    return events, total


def bati() -> tuple[list, float]:
    beat = 60 / 64
    events = []
    add_krar_bed(events, BATI, beat, 8, 62)
    line = [62, 65, 67, 69, 72, 69, 67, 65, 67, 65, 62, 65, 69, 67, 65, 62]
    for i, note in enumerate(line):
        events.append((i * beat * 1.7, "masenqo", note, beat * 1.65, 0.32))
    total = 8 * 4 * beat + 1.4
    return events, total


def ambassel() -> tuple[list, float]:
    beat = 60 / 76
    events = []
    add_krar_bed(events, AMBASSEL, beat, 10, 62)
    line = [70, 69, 67, 63, 62, 63, 67, 69, 70, 67, 63, 62, 67, 69, 70, 69, 67, 62]
    for i, note in enumerate(line):
        events.append((i * beat * 1.55 + 0.2, "washint", note, beat * 1.4, 0.3))
    total = 10 * 4 * beat + 1.0
    return events, total


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


def main() -> None:
    for name, builder in (("tizita", tizita), ("bati", bati), ("ambassel", ambassel)):
        events, total = builder()
        print("render", name)
        write_mp3(name, mix(events, total))


if __name__ == "__main__":
    main()
