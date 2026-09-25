#!/usr/bin/env python3
"""Quiet classical pieces in Ethiopian qenet, for reading.

Soft tones only: slow attack, no noise, no bowed voice. The three qenet
stay distinct, and each one fades so a loop does not click.
"""

from __future__ import annotations

import array
import math
import struct
import subprocess
import wave
from pathlib import Path

SR = 22050
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "audio"
OUT.mkdir(parents=True, exist_ok=True)


def freq(midi: float) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def tone(midi: float, seconds: float) -> array.array:
    n = max(1, int(SR * seconds))
    out = array.array("f", [0.0]) * n
    f = freq(midi)
    for i in range(n):
        t = i / SR
        attack = min(1.0, t / 0.45)
        release = 1.0 if t < seconds - 0.9 else max(0.0, (seconds - t) / 0.9)
        env = attack * release * math.exp(-0.22 * t)
        phase = math.tau * f * t
        out[i] = (math.sin(phase) + 0.05 * math.sin(2 * phase)) * env
    return out


def mix(events: list[tuple], total: float) -> array.array:
    n = int(SR * total)
    buf = array.array("f", [0.0]) * n
    cache: dict[tuple, array.array] = {}
    for start, midi, dur, vel in events:
        key = (round(float(midi), 2), round(dur, 2))
        if key not in cache:
            cache[key] = tone(float(midi), dur)
        src = cache[key]
        i0 = int(start * SR)
        length = min(len(src), n - i0)
        for i in range(max(0, length)):
            buf[i0 + i] += vel * src[i]
    prev = 0.0
    for i in range(n):
        prev = prev * 0.12 + buf[i] * 0.88
        buf[i] = prev
    fade = int(SR * 1.6)
    for i in range(min(fade, n)):
        buf[i] *= i / fade
        buf[n - 1 - i] *= i / fade
    peak = max((abs(sample) for sample in buf), default=1) or 1
    scale = 0.58 / peak
    for i in range(n):
        buf[i] *= scale
    return buf


def lay(events: list, start: float, notes: list, beat: float, vel: float) -> None:
    t = start
    for item in notes:
        if item is None:
            t += beat
            continue
        note, dur = item
        events.append((t, note, dur * beat, vel))
        events.append((t, note - 12, dur * beat, vel * 0.28))
        t += dur * beat


def tizita() -> tuple[list, float]:
    beat = 60 / 48
    notes = [
        (62, 4), (66, 3), (64, 3), (62, 4), None,
        (71, 3), (69, 2), (66, 3), (64, 4), (62, 5),
    ]
    events: list = []
    lay(events, 1.2, notes, beat, 0.34)
    lay(events, 1.2 + beat * 18, notes, beat, 0.3)
    return events, beat * 40 + 3


def bati() -> tuple[list, float]:
    beat = 60 / 52
    notes = [
        (62, 3), (65, 2), (67, 3), (69, 4), None,
        (72, 3), (69, 2), (67, 3), (65, 3), (62, 5),
    ]
    events: list = []
    lay(events, 1.0, notes, beat, 0.32)
    lay(events, 1.0 + beat * 16, [(67, 4), (69, 3), (65, 3), (62, 6)], beat, 0.28)
    return events, beat * 36 + 3


def ambassel() -> tuple[list, float]:
    beat = 60 / 56
    notes = [
        (62, 3), (63, 2), (67, 3), (69, 2), (70, 4), None,
        (69, 2), (67, 3), (63, 2), (62, 5),
    ]
    events: list = []
    lay(events, 1.0, notes, beat, 0.3)
    lay(events, 1.0 + beat * 17, notes, beat, 0.26)
    return events, beat * 38 + 3


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
        ["ffmpeg", "-y", "-i", str(wav_path), "-c:a", "libmp3lame", "-q:a", "5", str(mp3_path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    wav_path.unlink()
    print(name, mp3_path.stat().st_size)


def main() -> None:
    for name, builder in (("tizita", tizita), ("bati", bati), ("ambassel", ambassel)):
        events, total = builder()
        print("render", name, round(total, 1))
        write_mp3(name, mix(events, total))


if __name__ == "__main__":
    main()
