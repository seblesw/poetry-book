#!/usr/bin/env python3
"""Render one editorial story plate per poem, plus the cover.

These are original graphic plates. The source document has no photographs.
Replace public/plates/*.jpg when real photography is available; poem JSON
already points at these paths.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "plates"
TMP = ROOT / ".cache" / "plates"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)


def svg(c1: str, c2: str, c3: str, glow: str, body: str, gid: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1200">
  <defs>
    <linearGradient id="bg{gid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset="0.58" stop-color="{c2}"/>
      <stop offset="1" stop-color="{c3}"/>
    </linearGradient>
    <radialGradient id="gl{gid}" cx="48%" cy="42%" r="58%">
      <stop offset="0" stop-color="{glow}" stop-opacity="0.72"/>
      <stop offset="0.55" stop-color="{glow}" stop-opacity="0.16"/>
      <stop offset="1" stop-color="{glow}" stop-opacity="0"/>
    </radialGradient>
    <filter id="grain{gid}">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{gid}"/>
      <feColorMatrix type="saturate" values="0"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.22"/></feComponentTransfer>
    </filter>
  </defs>
  <rect width="900" height="1200" fill="url(#bg{gid})"/>
  <rect width="900" height="1200" fill="url(#gl{gid})"/>
  {body}
  <rect width="900" height="1200" filter="url(#grain{gid})" opacity="0.28"/>
  <rect x="48" y="48" width="804" height="1104" fill="none" stroke="#F7F1E8" stroke-opacity="0.28" stroke-width="1.5"/>
</svg>'''


def window(x, y, w, h, fill="#140C09", light="#F6E2C4", opacity=0.9):
    return f'''
      <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" opacity="{opacity}"/>
      <rect x="{x+18}" y="{y+18}" width="{w-36}" height="{h*0.62}" fill="{light}" opacity="0.88"/>
      <rect x="{x}" y="{y+h*0.48}" width="{w}" height="8" fill="#1A0E0A" opacity="0.55"/>
      <rect x="{x+w*0.48}" y="{y}" width="8" height="{h}" fill="#1A0E0A" opacity="0.45"/>
    '''


PLATES: dict[str, str] = {}

PLATES["cover"] = svg("#1A0E0A", "#3C2418", "#8A5A32", "#E7C7A1", f'''
  <ellipse cx="450" cy="620" rx="250" ry="340" fill="#2B1710" opacity="0.55"/>
  <path d="M450 250 C450 250 470 520 450 980" stroke="#C4A574" stroke-width="3" fill="none" opacity="0.8"/>
  <path d="M250 430 C340 390 400 520 450 560 C500 520 560 390 650 430 C600 620 520 700 450 760 C380 700 300 620 250 430Z" fill="#F7F1E8" opacity="0.9"/>
  <path d="M450 470 C470 560 470 680 450 760 C430 680 430 560 450 470Z" fill="#2B1710" opacity="0.85"/>
  <circle cx="450" cy="430" r="18" fill="#C4A574"/>
''', "cover")

PLATES["01"] = svg("#1A0E0A", "#5C3A28", "#8C6248", "#E8C9A4", f'''
  {window(520, 180, 250, 340)}
  <rect x="180" y="760" width="150" height="18" fill="#F7F1E8" opacity="0.85"/>
  <rect x="210" y="620" width="22" height="160" fill="#F7F1E8" opacity="0.8"/>
  <rect x="278" y="620" width="22" height="160" fill="#F7F1E8" opacity="0.8"/>
  <path d="M168 620 H340 L318 560 H190 Z" fill="#F3E6D4"/>
  <ellipse cx="300" cy="900" rx="120" ry="16" fill="#000" opacity="0.28"/>
''', "01")

PLATES["02"] = svg("#120E14", "#3A2430", "#6A4038", "#F0D2B0", '''
  <rect x="330" y="280" width="240" height="460" rx="28" fill="#1A1014"/>
  <rect x="352" y="330" width="196" height="340" rx="8" fill="#F6E1C8" opacity="0.92"/>
  <rect x="372" y="360" width="120" height="10" fill="#2B1710" opacity="0.35"/>
  <rect x="372" y="386" width="156" height="10" fill="#2B1710" opacity="0.2"/>
  <rect x="372" y="412" width="90" height="10" fill="#2B1710" opacity="0.2"/>
  <circle cx="450" cy="700" r="16" fill="#C4A574" opacity="0.8"/>
  <path d="M250 860 C340 800 560 800 650 860" stroke="#E7C7A1" stroke-width="2" fill="none" opacity="0.5"/>
''', "02")

PLATES["03"] = svg("#1C1410", "#6A4030", "#A36A48", "#F3E1C8", '''
  <path d="M180 780 C280 420 360 360 450 520" stroke="#F7F1E8" stroke-width="18" fill="none" stroke-linecap="round" opacity="0.9"/>
  <path d="M720 780 C620 420 540 360 450 520" stroke="#E8C9A4" stroke-width="18" fill="none" stroke-linecap="round" opacity="0.75"/>
  <circle cx="450" cy="520" r="16" fill="#C4A574"/>
  <circle cx="450" cy="520" r="70" fill="none" stroke="#F7F1E8" stroke-opacity="0.35"/>
''', "03")

PLATES["04"] = svg("#2A140C", "#8A4A22", "#C4783A", "#F6D7A8", '''
  <g fill="#F8E6C8" opacity="0.9">
    <circle cx="220" cy="300" r="8"/><circle cx="300" cy="240" r="5"/>
    <circle cx="640" cy="280" r="7"/><circle cx="700" cy="360" r="4"/>
    <circle cx="520" cy="220" r="6"/><circle cx="400" cy="260" r="3"/>
  </g>
  <path d="M250 860 C310 700 360 640 450 600 C470 560 500 520 560 500 L620 470" stroke="#1A0E0A" stroke-width="16" fill="none" stroke-linecap="round"/>
  <ellipse cx="610" cy="455" rx="46" ry="28" fill="#F7F1E8" transform="rotate(-28 610 455)"/>
  <path d="M560 500 L650 430" stroke="#C4A574" stroke-width="6" stroke-linecap="round"/>
''', "04")

PLATES["05"] = svg("#3A2414", "#C47A3A", "#E0A060", "#F8E2C0", '''
  <path d="M0 860 H900 L900 1200 H0Z" fill="#2B1710" opacity="0.45"/>
  <path d="M80 860 L340 1040" stroke="#1A0E0A" stroke-width="28" stroke-linecap="round"/>
  <path d="M820 860 L560 1080" stroke="#1A0E0A" stroke-width="28" stroke-linecap="round"/>
  <circle cx="450" cy="340" r="70" fill="#F6E2C4" opacity="0.95"/>
''', "05")

PLATES["06"] = svg("#1A1014", "#5A3040", "#8A5060", "#F0C8C0", '''
  <path d="M250 560 C250 430 340 360 450 360 C560 360 650 430 650 560 C650 700 450 820 450 820 C450 820 250 700 250 560Z" fill="none" stroke="#F7F1E8" stroke-width="10"/>
  <circle cx="450" cy="540" r="46" fill="#F7F1E8" opacity="0.92"/>
  <circle cx="450" cy="540" r="18" fill="#2B1710"/>
  <path d="M160 980 H300 L340 940 H400 L450 1000 L500 900 H560 L600 960 H760" stroke="#E8C9A4" stroke-width="4" fill="none"/>
''', "06")

PLATES["07"] = svg("#1A140E", "#3A4A62", "#6A5A48", "#F6E2B8", '''
  <circle cx="320" cy="460" r="90" fill="#F6E2B8"/>
  <circle cx="560" cy="420" r="70" fill="none" stroke="#F7F1E8" stroke-width="14"/>
  <path d="M0 860 C200 800 400 900 900 760 L900 1200 L0 1200Z" fill="#1A0E0A" opacity="0.55"/>
''', "07")

PLATES["08"] = svg("#101014", "#2A2A32", "#4A4038", "#C8C0B4", '''
  <rect x="250" y="700" width="400" height="16" fill="#F7F1E8" opacity="0.25"/>
  <rect x="300" y="560" width="300" height="150" rx="18" fill="#1A1818"/>
  <rect x="300" y="560" width="300" height="18" fill="#3A3634"/>
  <circle cx="450" cy="500" r="6" fill="#8A8078" opacity="0.4"/>
''', "08")

PLATES["09"] = svg("#1A2218", "#3E5A38", "#6A7040", "#E4D2B0", '''
  <rect x="300" y="640" width="28" height="320" fill="#2B2116"/>
  <rect x="560" y="700" width="24" height="260" fill="#2B2116"/>
  <ellipse cx="314" cy="560" rx="120" ry="160" fill="#1E2A1C" opacity="0.9"/>
  <ellipse cx="572" cy="620" rx="100" ry="130" fill="#243024" opacity="0.9"/>
  <ellipse cx="430" cy="500" rx="70" ry="90" fill="#314232" opacity="0.75"/>
  <rect x="0" y="940" width="900" height="260" fill="#14180F"/>
''', "09")

PLATES["10"] = svg("#1A1210", "#6A5040", "#A08068", "#F6E6D4", '''
  <rect x="300" y="260" width="300" height="620" fill="#2B1710"/>
  <rect x="330" y="300" width="110" height="540" fill="#1A0E0A"/>
  <rect x="460" y="300" width="110" height="540" fill="#1A0E0A"/>
  <rect x="438" y="300" width="24" height="540" fill="#C4A574" opacity="0.85"/>
  <path d="M0 0 H220 V1200 H0Z" fill="#F6E6D4" opacity="0.18"/>
''', "10")

PLATES["11"] = svg("#2A1814", "#8A5848", "#C48870", "#F8E0D0", '''
  <circle cx="450" cy="430" r="120" fill="#2B1710" opacity="0.9"/>
  <path d="M300 860 C340 700 390 640 450 640 C510 640 560 700 600 860 L560 860 C530 760 500 710 450 710 C400 710 370 760 340 860Z" fill="#2B1710"/>
  <path d="M180 760 C260 700 320 740 360 800" stroke="#F7F1E8" stroke-width="22" fill="none" stroke-linecap="round" opacity="0.85"/>
''', "11")

PLATES["12"] = svg("#241810", "#A07048", "#D0A070", "#F4E4CC", '''
  <rect x="160" y="280" width="580" height="560" fill="none" stroke="#F7F1E8" stroke-width="10" opacity="0.8"/>
  <path d="M160 560 H740" stroke="#F7F1E8" stroke-width="8" opacity="0.45"/>
  <circle cx="300" cy="760" r="36" fill="#2B1710"/>
  <rect x="284" y="790" width="32" height="120" fill="#2B1710"/>
  <circle cx="600" cy="780" r="30" fill="#2B1710" opacity="0.75"/>
  <rect x="586" y="806" width="28" height="90" fill="#2B1710" opacity="0.75"/>
''', "12")

PLATES["13"] = svg("#2A1A12", "#6A4030", "#A06848", "#F8E6D0", '''
  <rect x="140" y="720" width="620" height="28" fill="#F7F1E8" opacity="0.88"/>
  <rect x="180" y="748" width="22" height="180" fill="#F7F1E8" opacity="0.5"/>
  <rect x="700" y="748" width="22" height="180" fill="#F7F1E8" opacity="0.5"/>
  <ellipse cx="450" cy="640" rx="70" ry="28" fill="#F3E6D4"/>
  <path d="M430 620 C440 540 470 500 500 440" stroke="#F7F1E8" stroke-width="6" fill="none" opacity="0.7"/>
  <path d="M450 610 C470 520 450 470 490 400" stroke="#F7F1E8" stroke-width="4" fill="none" opacity="0.45"/>
  <circle cx="250" cy="360" r="40" fill="#E8C9A4" opacity="0.35"/>
''', "13")

PLATES["14"] = svg("#2A1418", "#704048", "#A06058", "#F6D8D0", '''
  <circle cx="400" cy="560" r="70" fill="#F4D6CC"/>
  <circle cx="330" cy="500" r="36" fill="#E8B0A8"/>
  <circle cx="470" cy="490" r="32" fill="#E8B0A8"/>
  <circle cx="360" cy="620" r="30" fill="#E8B0A8"/>
  <circle cx="450" cy="630" r="28" fill="#E8B0A8"/>
  <rect x="392" y="620" width="16" height="220" fill="#2B1710"/>
  <path d="M620 260 L760 980" stroke="#1A0E0A" stroke-width="26" opacity="0.55"/>
''', "14")

PLATES["15"] = svg("#141820", "#3A4A58", "#607080", "#D8E0E6", '''
  ''' + window(230, 180, 440, 560, "#0E141C", "#D5DEE6", 0.95) + '''
  <g stroke="#E7EEF2" stroke-width="3" opacity="0.55">
    <path d="M260 220 L240 520"/><path d="M320 200 L300 560"/>
    <path d="M390 210 L370 540"/><path d="M460 190 L450 580"/>
    <path d="M530 210 L520 560"/><path d="M600 200 L590 520"/>
  </g>
  <rect x="180" y="860" width="540" height="80" fill="#101820" opacity="0.65"/>
''', "15")

PLATES["16"] = svg("#2A2018", "#C47840", "#E0A060", "#F6E0C8", '''
  <path d="M0 900 H900 V1200 H0Z" fill="#2B1710" opacity="0.35"/>
  <circle cx="250" cy="760" r="28" fill="#1A0E0A"/>
  <path d="M230 800 L180 980" stroke="#1A0E0A" stroke-width="16" stroke-linecap="round"/>
  <path d="M250 820 L340 900" stroke="#1A0E0A" stroke-width="16" stroke-linecap="round"/>
  <path d="M640 820 C690 800 720 840 700 880 C680 900 640 890 630 860" fill="#1A0E0A"/>
  <circle cx="700" cy="800" r="16" fill="#1A0E0A"/>
  <rect x="688" y="816" width="14" height="40" fill="#1A0E0A"/>
''', "16")

PLATES["17"] = svg("#100C0A", "#3A2418", "#5A3820", "#F8D9A0", '''
  <rect x="400" y="620" width="28" height="160" fill="#F3E6D4" opacity="0.85"/>
  <path d="M414 620 C390 560 430 500 414 440 C450 520 470 560 430 620Z" fill="#F6C56A"/>
  <ellipse cx="450" cy="500" rx="160" ry="200" fill="#F8D9A0" opacity="0.13"/>
  <path d="M120 980 H780" stroke="#F7F1E8" stroke-width="2" opacity="0.2"/>
  <rect x="160" y="240" width="80" height="120" fill="#F7F1E8" opacity="0.05"/>
  <rect x="660" y="300" width="70" height="160" fill="#F7F1E8" opacity="0.05"/>
''', "17")

PLATES["18"] = svg("#12141A", "#2A3344", "#465066", "#C8D4E4", '''
  <rect x="180" y="240" width="200" height="320" rx="16" fill="#D5DDEA" opacity="0.85"/>
  <rect x="410" y="300" width="160" height="250" rx="14" fill="#C5D0E0" opacity="0.55"/>
  <rect x="600" y="360" width="120" height="180" rx="12" fill="#B7C4D6" opacity="0.35"/>
  <rect x="430" y="860" width="120" height="14" fill="#F7F1E8" opacity="0.7"/>
  <rect x="470" y="760" width="18" height="110" fill="#F7F1E8" opacity="0.55"/>
  <path d="M430 760 H540 L520 720 H450 Z" fill="#F7F1E8" opacity="0.75"/>
''', "18")

PLATES["19"] = svg("#1A1418", "#5A4060", "#8A6878", "#F0D8E0", '''
  <path d="M180 700 C260 500 300 420 380 480 C300 560 280 640 320 760" stroke="#F7F1E8" stroke-width="3" fill="none" opacity="0.7"/>
  <path d="M700 640 C620 460 540 400 500 500 C580 540 640 620 600 760" stroke="#F7F1E8" stroke-width="3" fill="none" opacity="0.55"/>
  <path d="M250 820 C360 700 540 700 650 820" stroke="#F6E6EA" stroke-width="16" fill="none" stroke-linecap="round"/>
  <path d="M310 860 C400 780 500 780 590 860" stroke="#F6E6EA" stroke-width="16" fill="none" stroke-linecap="round"/>
  <circle cx="450" cy="430" r="54" fill="#F7F1E8" opacity="0.9"/>
''', "19")

PLATES["20"] = svg("#241610", "#6A4030", "#A06840", "#F4E0C8", '''
  <ellipse cx="450" cy="700" rx="150" ry="40" fill="#F7F1E8"/>
  <path d="M310 700 C310 820 590 820 590 700" fill="#2B1710"/>
  <ellipse cx="450" cy="700" rx="110" ry="26" fill="#3C2418"/>
  <path d="M420 660 C430 560 470 500 450 420" stroke="#F7F1E8" stroke-width="5" fill="none" opacity="0.75"/>
  <path d="M460 650 C500 560 480 490 520 420" stroke="#F7F1E8" stroke-width="4" fill="none" opacity="0.5"/>
  <path d="M400 640 C360 540 390 470 340 400" stroke="#E8C9A4" stroke-width="3" fill="none" opacity="0.45"/>
''', "20")

PLATES["21"] = svg("#181614", "#4A4440", "#6A625C", "#E8E0D6", '''
  <rect x="250" y="340" width="280" height="200" rx="16" fill="#1A1614"/>
  <circle cx="390" cy="440" r="62" fill="#2A2624"/>
  <circle cx="390" cy="440" r="34" fill="#C8B8A4" opacity="0.85"/>
  <circle cx="390" cy="440" r="14" fill="#1A0E0A"/>
  <rect x="470" y="360" width="40" height="28" fill="#C4A574"/>
  <circle cx="640" cy="760" r="40" fill="#E8E0D6" opacity="0.8"/>
  <path d="M610 820 C630 900 700 940 760 900" stroke="#E8E0D6" stroke-width="22" fill="none" stroke-linecap="round" opacity="0.75"/>
''', "21")

PLATES["22"] = svg("#1A1814", "#8A7A62", "#C4B498", "#F6EFE4", '''
  <path d="M450 280 L700 980 H200 Z" fill="#EFE6D8" opacity="0.18"/>
  <rect x="300" y="700" width="200" height="130" rx="8" fill="#F7F1E8" opacity="0.88"/>
  <path d="M300 730 H500" stroke="#2B1710" stroke-width="8"/>
  <rect x="360" y="640" width="16" height="70" fill="#F7F1E8"/>
  <circle cx="450" cy="360" r="48" fill="#F6EFE4" opacity="0.9"/>
''', "22")

PLATES["23"] = svg("#1C1614", "#5A4840", "#8A7060", "#F4E8DC", '''
  <ellipse cx="360" cy="520" rx="130" ry="180" fill="none" stroke="#F7F1E8" stroke-width="12"/>
  <ellipse cx="360" cy="520" rx="90" ry="130" fill="#F4E8DC" opacity="0.12"/>
  <rect x="520" y="620" width="220" height="140" fill="#F7F1E8"/>
  <path d="M520 620 L630 710 L740 620" fill="#E4D3C2"/>
  <circle cx="630" cy="700" r="8" fill="#C4A574"/>
''', "23")

PLATES["24"] = svg("#221814", "#6A5040", "#8A6848", "#F0DCC8", '''
  <g fill="#F7F1E8">
    <rect x="140" y="360" width="16" height="280" opacity="0.35"/>
    <rect x="190" y="320" width="16" height="340" opacity="0.5"/>
    <rect x="240" y="390" width="16" height="250" opacity="0.3"/>
    <rect x="300" y="300" width="18" height="380" opacity="0.7"/>
    <rect x="360" y="340" width="16" height="300" opacity="0.45"/>
    <rect x="430" y="280" width="18" height="400" opacity="0.8"/>
    <rect x="500" y="360" width="16" height="280" opacity="0.4"/>
    <rect x="560" y="320" width="16" height="340" opacity="0.55"/>
  </g>
  <rect x="600" y="700" width="140" height="150" rx="10" fill="#1A0E0A" opacity="0.8"/>
  <rect x="620" y="760" width="100" height="70" fill="#C4A574" opacity="0.85"/>
''', "24")

PLATES["25"] = svg("#1A1810", "#5A6840", "#8A8850", "#F0E6C8", '''
  <path d="M450 1040 L450 620" stroke="#F7F1E8" stroke-width="16" stroke-linecap="round"/>
  <path d="M450 620 L240 340" stroke="#F7F1E8" stroke-width="16" stroke-linecap="round"/>
  <path d="M450 620 L680 300" stroke="#E8D7A8" stroke-width="16" stroke-linecap="round"/>
  <circle cx="240" cy="330" r="18" fill="#C4A574"/>
  <circle cx="690" cy="290" r="18" fill="#F7F1E8"/>
''', "25")

PLATES["26"] = svg("#2A1420", "#8A3A40", "#C06048", "#F8D0C0", '''
  <rect x="0" y="0" width="450" height="1200" fill="#6A2430" opacity="0.45"/>
  <circle cx="230" cy="420" r="80" fill="#F6C7A8" opacity="0.9"/>
  <g fill="#F8D8C4" opacity="0.8">
    <circle cx="140" cy="300" r="6"/><circle cx="300" cy="260" r="4"/><circle cx="180" cy="240" r="3"/>
  </g>
  <rect x="450" y="0" width="450" height="1200" fill="#EFE6DA" opacity="0.16"/>
  <circle cx="670" cy="460" r="54" fill="#F7F1E8" opacity="0.55"/>
  <path d="M520 860 H820" stroke="#F7F1E8" stroke-width="2" opacity="0.35"/>
''', "26")

PLATES["27"] = svg("#1A1412", "#5A4038", "#8A6858", "#F6E4D4", '''
  <ellipse cx="300" cy="760" rx="70" ry="18" fill="#F7F1E8"/>
  <path d="M236 760 C236 820 364 820 364 760" fill="#2B1710" opacity="0.85"/>
  <ellipse cx="620" cy="760" rx="70" ry="18" fill="#F7F1E8" opacity="0.45"/>
  <path d="M556 760 C556 820 684 820 684 760" fill="#2B1710" opacity="0.45"/>
  <rect x="400" y="520" width="120" height="200" rx="14" fill="#F6E1C8"/>
  <rect x="414" y="540" width="92" height="150" fill="#2B1710" opacity="0.8"/>
''', "27")

PLATES["28"] = svg("#1E1814", "#A08058", "#E6Cba0".replace("a", "A") if False else "#C4A070", "#FFF6EA", '''
  <rect x="180" y="700" width="150" height="16" fill="#F7F1E8"/>
  <rect x="210" y="560" width="18" height="150" fill="#F7F1E8"/>
  <rect x="282" y="560" width="18" height="150" fill="#F7F1E8"/>
  <path d="M170 560 H340 L318 510 H192 Z" fill="#FFFDF8"/>
  <rect x="570" y="700" width="150" height="16" fill="#F7F1E8"/>
  <rect x="600" y="560" width="18" height="150" fill="#F7F1E8"/>
  <rect x="672" y="560" width="18" height="150" fill="#F7F1E8"/>
  <path d="M560 560 H730 L708 510 H582 Z" fill="#FFFDF8"/>
  <circle cx="450" cy="360" r="64" fill="#FFF6EA" opacity="0.95"/>
''', "28")

PLATES["end"] = svg("#1A0E0A", "#3C2418", "#6B442C", "#E7C7A1", '''
  <circle cx="450" cy="560" r="150" fill="none" stroke="#F7F1E8" stroke-width="2" opacity="0.7"/>
  <circle cx="450" cy="560" r="8" fill="#C4A574"/>
  <path d="M450 250 V430" stroke="#C4A574" stroke-width="2"/>
  <path d="M450 690 V910" stroke="#C4A574" stroke-width="2"/>
''', "end")


def main() -> None:
    for key, markup in PLATES.items():
        svg_path = TMP / f"{key}.svg"
        jpg_path = OUT / f"{key}.jpg"
        svg_path.write_text(markup, encoding="utf-8")
        subprocess.run(
            [
                "magick",
                "-background",
                "#1A0E0A",
                str(svg_path),
                "-resize",
                "1200x1600",
                "-quality",
                "86",
                str(jpg_path),
            ],
            check=True,
        )
        print(jpg_path.name, jpg_path.stat().st_size)


if __name__ == "__main__":
    main()
