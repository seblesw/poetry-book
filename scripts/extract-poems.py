#!/usr/bin/env python3
"""Extract poems from the source .docx into content/poems.json.

The Word file is the editorial source. UI components never contain poem text.
"""

from __future__ import annotations

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "የግጥም መድብል#1.docx"
OUT = ROOT / "content" / "poems.json"
TITLE_RE = re.compile(r"^\s*ርዕስ\s*[-:፦.]*\s*")


def paragraph_text(p: ET.Element) -> str:
    parts: list[str] = []
    for el in p.iter():
        tag = el.tag
        if tag == f"{W}t" and el.text:
            parts.append(el.text)
        elif tag == f"{W}br":
            parts.append("\n")
        elif tag == f"{W}tab":
            parts.append("\t")
    return "".join(parts)


def clean_lines(text: str) -> list[str]:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return [line for line in lines if line.strip() != "."]


def excerpt(text: str, limit: int = 90) -> str:
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped:
            return stripped if len(stripped) <= limit else stripped[: limit - 1].rstrip() + "…"
    return ""


def main() -> None:
    with zipfile.ZipFile(DOCX) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))

    blocks = []
    for p in root.iter(f"{W}p"):
        text = paragraph_text(p)
        if text.strip():
            blocks.append(text)

    if not blocks or "ግጥሞች" not in blocks[0]:
        raise SystemExit("Expected the collection title in the first paragraph.")

    poems = []
    current: dict | None = None

    def flush() -> None:
        nonlocal current
        if not current:
            return
        text = "\n".join(current["lines"]).strip("\n")
        if not current["title"] or not text:
            raise SystemExit(f"Incomplete poem: {current!r}")
        number = len(poems) + 1
        poems.append(
            {
                "id": str(number),
                "number": number,
                "slug": str(number),
                "title": current["title"],
                "text": text,
                "image": f"/plates/{number:02d}.jpg",
                "alt": current["alt"],
                "description": excerpt(text),
            }
        )
        current = None

    # Visual alts are filled by the plate script's companion map below.
    alts = ALT_BY_ORDER

    for block in blocks[1:]:
        lines = clean_lines(block)
        if not lines:
            continue
        if TITLE_RE.match(lines[0]):
            flush()
            title = TITLE_RE.sub("", lines[0]).strip()
            if not title:
                raise SystemExit(f"Empty title in block: {lines[0]!r}")
            rest = lines[1:]
            current = {
                "title": title,
                "lines": rest,
                "alt": alts[len(poems)],
            }
            continue
        if current is None:
            raise SystemExit(f"Body before a title: {lines[0]!r}")
        # Separate Word paragraphs are layout breaks, not authored stanza gaps.
        current["lines"].extend(lines)

    flush()
    if len(poems) != 28:
        raise SystemExit(f"Expected 28 poems, extracted {len(poems)}")

    payload = {
        "source": "የግጥም መድብል#1.docx",
        "title": "አጫጭር የፍቅር ግጥሞች",
        "series": "የግጥም መድብል",
        "poems": poems,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(poems)} poems)")
    for poem in poems:
        print(f"{poem['number']:02d}  {poem['title']}  ({poem['text'].count(chr(10)) + 1} lines)")


# Order matches the document. These describe the editorial plates, not invented poem text.
ALT_BY_ORDER = [
    "ምሽት ላይ ባዶ ወንበርና የመስኮት ብርሃን፤ የተለየ ፍቅር ትዝታ።",
    "ጨለማ ውስጥ የሚበራ ስልክ፤ ሊዘጋ የማይችል ንግግር።",
    "ሁለት የብርሃን መስመሮች ሲገናኙ፤ የተሰረቀ እይታ።",
    "የበዓል ብርሃንና የመለከት ጥላ፤ የጥር ትዝታ።",
    "ወርቃማ መንገድ ላይ ሁለት ረጅም ጥላዎች።",
    "አንድ የዓይን ብርሃንና የልብ ምት መስመር።",
    "በአንድ ሰማይ ፀሐይና ጨረቃ፤ ቀንና ሌሊት።",
    "ጨለማ ጠረጴዛ ላይ ፊቱን የጣለ ዝም ያለ ስልክ።",
    "አብረው የበቀሉ ሁለት ዛፎች፤ የልጅነት ትውውቅ።",
    "ዝግ በርና ቀጭን የንጋት ብርሃን።",
    "ዝቅ ያለ ራስና ሞቅ ያለ የእጅ ብርሃን።",
    "የጥዋት አደባባይ በር፤ ሁለት የተራራቁ ጥላዎች።",
    "የቡና ቤት ትነትና ሞቅ ያለ ቆጣሪ።",
    "አበባና ስለታም ጥላ፤ ምስጋናና መከፋት።",
    "ዝናብ በመስኮት ላይ፤ ቀዝቃዛ ባዶ ክፍል።",
    "ጎዳና፤ የሚሮጥ ጥላና ሩቅ ውሻ።",
    "ጨለማ ክፍል ውስጥ አንዲት የሰም ነበልባል።",
    "የተደራረቡ የስክሪን ብርሃኖችና ብቸኛ ወንበር።",
    "የተደናገሩ መስመሮች ወደ አንድ ዑደት ሲሰበሰቡ።",
    "የቡና ስኒና እንደ ሀሳብ የሚወጣ ትነት።",
    "ካሜራና ፊቱን የመለሰ ጥላ።",
    "ባዶ ቦርሳና ረጅም የንጋት መንገድ።",
    "መስታወትና የታሸገ ደብዳቤ።",
    "የሕዝብ መስመሮችና ኪስ።",
    "ወደ ሁለት የሚከፈል መንገድ።",
    "የቅዳሜ ሙቀትና የእሁድ ፈዛዛ ጠዋት።",
    "ሁለት ስኒዎች፤ አንደኛው ወደ ስልክ የተዘነበለ።",
    "ሁለት ወንበሮች በጠራ ብርሃን ተጋርጠው።",
]


if __name__ == "__main__":
    main()
