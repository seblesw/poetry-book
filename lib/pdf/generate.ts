import {
  PDFDocument,
  PDFFont,
  PDFHexString,
  PDFImage,
  PDFName,
  PDFPage,
  rgb,
} from "pdf-lib";
import fontkit from "@pdf-lib/fontkit";
import fs from "fs/promises";
import path from "path";
import { book } from "@/content/book";
import { poems, type Poem } from "@/lib/poems";

const PAGE_W = 841.89;
const PAGE_H = 595.28;
const HALF = PAGE_W / 2;

const INK = rgb(43 / 255, 23 / 255, 16 / 255);
const PAPER = rgb(247 / 255, 241 / 255, 232 / 255);
const CREAM = rgb(255 / 255, 253 / 255, 248 / 255);
const DARK = rgb(26 / 255, 14 / 255, 10 / 255);
const GOLD = rgb(196 / 255, 165 / 255, 116 / 255);
const MUTED = rgb(107 / 255, 83 / 255, 70 / 255);

const BODY = 18;
const LEAD = 34;
const BLANK = 16;
const TITLE = 32;
const TITLE_LEAD = 40;
const TEXT_X = HALF + 40;
const TEXT_W = HALF - 80;

type Fonts = {
  body: PDFFont;
  emoji: PDFFont;
  bodySet: Set<number>;
  emojiSet: Set<number>;
};

type Run = { text: string; font: PDFFont };

export type PdfTone = "light" | "dark";

type Ink = {
  paper: ReturnType<typeof rgb>;
  ink: ReturnType<typeof rgb>;
  muted: ReturnType<typeof rgb>;
  cream: ReturnType<typeof rgb>;
  ground: ReturnType<typeof rgb>;
  spine: ReturnType<typeof rgb>;
};

function toneOf(tone: PdfTone): Ink {
  if (tone === "dark") {
    return {
      paper: rgb(0.11, 0.07, 0.05),
      ink: rgb(0.97, 0.94, 0.9),
      muted: rgb(0.78, 0.7, 0.62),
      cream: rgb(0.97, 0.94, 0.9),
      ground: rgb(0.08, 0.05, 0.03),
      spine: rgb(0.24, 0.15, 0.1),
    };
  }
  return {
    paper: PAPER,
    ink: INK,
    muted: MUTED,
    cream: CREAM,
    ground: DARK,
    spine: rgb(0.16, 0.09, 0.06),
  };
}

const cached = new Map<PdfTone, Promise<Uint8Array>>();

export function getPoetryBookPdf(tone: PdfTone = "light"): Promise<Uint8Array> {
  const hit = cached.get(tone);
  if (hit) return hit;
  const job = build(tone).catch((error: unknown) => {
    cached.delete(tone);
    throw error;
  });
  cached.set(tone, job);
  return job;
}

async function build(tone: PdfTone): Promise<Uint8Array> {
  const ink = toneOf(tone);
  const pdf = await PDFDocument.create();
  pdf.registerFontkit(fontkit);

  const bodyBytes = await fs.readFile(path.join(process.cwd(), "assets/fonts/AbyssinicaSIL-R.ttf"));
  const emojiBytes = await fs.readFile(path.join(process.cwd(), "assets/fonts/NotoEmoji-Regular.ttf"));
  const body = await pdf.embedFont(bodyBytes, { subset: true });
  const emoji = await pdf.embedFont(emojiBytes, { subset: true });
  const fonts: Fonts = {
    body,
    emoji,
    bodySet: new Set(body.getCharacterSet()),
    emojiSet: new Set(emoji.getCharacterSet()),
  };

  const plates = new Map<string, PDFImage | null>();
  async function plate(file: string) {
    if (plates.has(file)) return plates.get(file) ?? null;
    try {
      const bytes = await fs.readFile(path.join(process.cwd(), "public", file.replace(/^\//, "")));
      const image = await pdf.embedJpg(bytes);
      plates.set(file, image);
      return image;
    } catch {
      plates.set(file, null);
      return null;
    }
  }

  const chunks = poems.map((poem) => chunkPoem(poem, fonts));
  const starts: number[] = [];
  const poemPdfIndex = new Map<string, number>();
  let cursor = 2;
  chunks.forEach((pages, index) => {
    starts.push(cursor - 2);
    poemPdfIndex.set(poems[index].id, cursor);
    cursor += pages.length;
  });
  const total = cursor + 1;

  const cover = pdf.addPage([PAGE_W, PAGE_H]);
  const tocPage = pdf.addPage([PAGE_W, PAGE_H]);
  const poemPages: PDFPage[] = [];
  chunks.forEach((pages) => {
    pages.forEach(() => poemPages.push(pdf.addPage([PAGE_W, PAGE_H])));
  });
  const endPage = pdf.addPage([PAGE_W, PAGE_H]);

  drawCover(cover, await plate(book.coverImage), fonts, ink);
  const tocLinks = drawToc(tocPage, fonts, poemPdfIndex, poemPages, starts, 2, ink);
  addLinks(pdf, tocPage, tocLinks);

  let drawn = 0;
  for (let i = 0; i < poems.length; i += 1) {
    const image = await plate(poems[i].image);
    chunks[i].forEach((lines, part) => {
      drawPoemSpread(poemPages[drawn], poems[i], lines, part === 0, image, fonts, poemPdfIndex.get(poems[i].id)! + part + 1, ink);
      drawn += 1;
    });
  }
  drawEnd(endPage, await plate(book.endImage), fonts, total, ink);

  addOutlines(pdf, [
    { title: "ሽፋን", page: cover },
    { title: "ማውጫ", page: tocPage },
    ...poems.map((poem, index) => ({
      title: `${String(poem.number).padStart(2, "0")}  ${poem.title}`,
      page: poemPages[chunks.slice(0, index).reduce((sum, pages) => sum + pages.length, 0)],
    })),
    { title: "መጨረሻ", page: endPage },
  ]);

  pdf.setTitle(book.title);
  pdf.setAuthor(book.poet);
  pdf.setSubject("Poetry / Digital Poetry Book");
  pdf.setKeywords(book.keywords);
  pdf.setLanguage("am");
  pdf.setCreator(book.title);
  pdf.setProducer(book.series);

  return pdf.save();
}

function runsOf(text: string, fonts: Fonts): Run[] {
  const runs: Run[] = [];
  let current: Run | null = null;
  for (const ch of Array.from(text)) {
    const cp = ch.codePointAt(0)!;
    const font = fonts.bodySet.has(cp) ? fonts.body : fonts.emojiSet.has(cp) ? fonts.emoji : null;
    if (!font) continue;
    if (!current || current.font !== font) {
      current = { text: ch, font };
      runs.push(current);
    } else {
      current.text += ch;
    }
  }
  return runs;
}

function widthOf(text: string, fonts: Fonts, size: number) {
  return runsOf(text, fonts).reduce((sum, run) => sum + run.font.widthOfTextAtSize(run.text, size), 0);
}

function drawRuns(
  page: PDFPage,
  text: string,
  x: number,
  y: number,
  size: number,
  color: ReturnType<typeof rgb>,
  fonts: Fonts,
  bold = false,
) {
  let cursor = x;
  for (const run of runsOf(text, fonts)) {
    page.drawText(run.text, { x: cursor, y, size, font: run.font, color });
    if (bold) page.drawText(run.text, { x: cursor + 0.32, y, size, font: run.font, color });
    cursor += run.font.widthOfTextAtSize(run.text, size);
  }
}

function wrap(text: string, fonts: Fonts, size: number, max: number): string[] {
  if (!text) return [""];
  if (widthOf(text, fonts, size) <= max) return [text];
  const lines: string[] = [];
  let buf = "";
  for (const ch of Array.from(text)) {
    const next = buf + ch;
    if (buf && widthOf(next, fonts, size) > max) {
      lines.push(buf.replace(/\s+$/u, ""));
      buf = /\s/u.test(ch) ? "" : ch;
    } else {
      buf = next;
    }
  }
  if (buf.trim()) lines.push(buf.replace(/\s+$/u, ""));
  return lines.length ? lines : [""];
}

function wrapWords(text: string, fonts: Fonts, size: number, max: number): string[] {
  const lines: string[] = [];
  let buf = "";
  for (const word of text.split(/\s+/u).filter(Boolean)) {
    const next = buf ? `${buf} ${word}` : word;
    if (widthOf(next, fonts, size) <= max) {
      buf = next;
      continue;
    }
    if (buf) lines.push(buf);
    if (widthOf(word, fonts, size) > max) {
      const parts = wrap(word, fonts, size, max);
      lines.push(...parts.slice(0, -1));
      buf = parts.at(-1) ?? "";
    } else {
      buf = word;
    }
  }
  if (buf) lines.push(buf);
  return lines.length ? lines : [""];
}

function fit(text: string, fonts: Fonts, size: number, max: number) {
  if (widthOf(text, fonts, size) <= max) return text;
  let value = text;
  while (value && widthOf(`${value}…`, fonts, size) > max) {
    value = Array.from(value).slice(0, -1).join("");
  }
  return `${value}…`;
}

function chunkPoem(poem: Poem, fonts: Fonts): string[][] {
  const flat: string[] = [];
  for (const raw of poem.text.split("\n")) {
    if (!raw.trim()) {
      flat.push("");
      continue;
    }
    flat.push(...wrapWords(raw, fonts, BODY, TEXT_W));
  }

  const pages: string[][] = [];
  let page: string[] = [];
  let used = 0;

  const capacity = () => {
    const header = pages.length === 0 ? headerHeight(poem.title, fonts) : 36;
    return PAGE_H - 50 - header - 48;
  };

  for (const line of flat) {
    const height = line === "" ? BLANK : LEAD;
    if (page.length && used + height > capacity()) {
      pages.push(page);
      page = [];
      used = 0;
    }
    page.push(line);
    used += height;
  }
  if (page.length) pages.push(page);
  return pages.length ? pages : [[""]];
}

function headerHeight(title: string, fonts: Fonts) {
  return wrapWords(title, fonts, TITLE, TEXT_W).length * TITLE_LEAD + 26;
}

function paintImage(page: PDFPage, image: PDFImage | null, box: { x: number; y: number; w: number; h: number }, fallback: string, fonts: Fonts, ink: Ink) {
  page.drawRectangle({ x: box.x, y: box.y, width: box.w, height: box.h, color: ink.ground });
  if (!image) {
    drawRuns(page, fallback, box.x + 28, box.y + box.h / 2, 28, ink.cream, fonts);
    return;
  }
  const scale = Math.min(box.w / image.width, box.h / image.height);
  const w = image.width * scale;
  const h = image.height * scale;
  page.drawImage(image, {
    x: box.x + (box.w - w) / 2,
    y: box.y + (box.h - h) / 2,
    width: w,
    height: h,
  });
}

function maskSpread(page: PDFPage, ink: Ink) {
  page.drawRectangle({ x: 0, y: 0, width: 14, height: PAGE_H, color: ink.paper });
  page.drawRectangle({ x: 0, y: 0, width: HALF, height: 14, color: ink.paper });
  page.drawRectangle({ x: 0, y: PAGE_H - 14, width: HALF, height: 14, color: ink.paper });
  page.drawRectangle({ x: HALF - 8, y: 0, width: PAGE_W - HALF + 8, height: PAGE_H, color: ink.paper });
  page.drawRectangle({ x: HALF - 9, y: 0, width: 18, height: PAGE_H, color: ink.spine });
  page.drawRectangle({ x: HALF - 0.5, y: 0, width: 1, height: PAGE_H, color: GOLD });
}

function drawCover(page: PDFPage, image: PDFImage | null, fonts: Fonts, ink: Ink) {
  page.drawRectangle({ x: 0, y: 0, width: PAGE_W, height: PAGE_H, color: ink.paper });
  paintImage(page, image, { x: 0, y: 0, w: HALF, h: PAGE_H }, "", fonts, ink);
  page.drawRectangle({ x: HALF - 8, y: 0, width: PAGE_W - HALF + 8, height: PAGE_H, color: ink.paper });
  page.drawRectangle({ x: HALF - 1, y: 48, width: 1, height: PAGE_H - 96, color: GOLD });

  const x = HALF + 48;
  drawRuns(page, `${book.series}  ·  ${book.issue}`, x, 430, 12, GOLD, fonts);
  let y = 390;
  for (const line of wrap(book.title, fonts, 36, HALF - 96)) {
    drawRuns(page, line, x, y, 36, ink.ink, fonts);
    y -= 46;
  }
  page.drawRectangle({ x, y: 176, width: 64, height: 1.25, color: GOLD });
  let creditY = 150;
  for (const line of wrap(book.credit, fonts, 12, HALF - 96)) {
    drawRuns(page, line, x, creditY, 12, ink.ink, fonts);
    creditY -= 18;
  }
  drawRuns(page, book.date, x, creditY - 6, 12, ink.muted, fonts);
}

function drawToc(
  page: PDFPage,
  fonts: Fonts,
  poemPdfIndex: Map<string, number>,
  poemPages: PDFPage[],
  starts: number[],
  pageNo: number,
  ink: Ink,
) {
  page.drawRectangle({ x: 0, y: 0, width: PAGE_W, height: PAGE_H, color: ink.paper });
  drawRuns(page, "ማውጫ", 48, PAGE_H - 58, 22, ink.ink, fonts);
  page.drawRectangle({ x: 48, y: PAGE_H - 74, width: 56, height: 1.2, color: GOLD });

  const links: { rect: [number, number, number, number]; page: PDFPage }[] = [];
  poems.forEach((poem, index) => {
    const col = index < 14 ? 0 : 1;
    const row = index % 14;
    const x = 48 + col * 390;
    const y = PAGE_H - 112 - row * 32;
    const label = String(poem.number).padStart(2, "0");
    drawRuns(page, label, x, y, 11, GOLD, fonts);
    const title = fit(poem.title, fonts, 12, 250);
    drawRuns(page, title, x + 36, y, 12, ink.ink, fonts);
    const destLabel = String(poemPdfIndex.get(poem.id)! + 1);
    drawRuns(page, destLabel, x + 320, y, 10, ink.muted, fonts);
    links.push({ rect: [x, y - 6, x + 350, y + 16], page: poemPages[starts[index]] });
  });
  footer(page, fonts, pageNo, "center", ink);
  return links;
}

function drawPoemSpread(
  page: PDFPage,
  poem: Poem,
  lines: string[],
  first: boolean,
  image: PDFImage | null,
  fonts: Fonts,
  pageNo: number,
  ink: Ink,
) {
  page.drawRectangle({ x: 0, y: 0, width: PAGE_W, height: PAGE_H, color: ink.paper });
  paintImage(page, image, { x: 0, y: 0, w: HALF, h: PAGE_H }, String(poem.number).padStart(2, "0"), fonts, ink);
  maskSpread(page, ink);

  let y = PAGE_H - 50;
  if (first) {
    for (const line of wrapWords(poem.title, fonts, TITLE, TEXT_W)) {
      drawRuns(page, line, TEXT_X, y, TITLE, ink.ink, fonts, true);
      y -= TITLE_LEAD;
    }
    y -= 6;
    page.drawRectangle({ x: TEXT_X, y: y + 12, width: 64, height: 1.15, color: GOLD });
    y -= 20;
  } else {
    drawRuns(page, fit(poem.title, fonts, 11, TEXT_W - 70), TEXT_X, y, 11, ink.muted, fonts);
    drawRuns(page, "ቀጣይ", PAGE_W - 78, y, 10, GOLD, fonts);
    y -= 36;
  }

  for (const line of lines) {
    if (!line) {
      y -= BLANK;
      continue;
    }
    drawRuns(page, line, TEXT_X, y, BODY, ink.ink, fonts, true);
    y -= LEAD;
  }

  const mark = String(poem.number).padStart(2, "0");
  drawRuns(page, mark, PAGE_W - 58, 32, 11, ink.muted, fonts);
  footer(page, fonts, pageNo, "spread", ink);
}

function drawEnd(page: PDFPage, image: PDFImage | null, fonts: Fonts, pageNo: number, ink: Ink) {
  page.drawRectangle({ x: 0, y: 0, width: PAGE_W, height: PAGE_H, color: ink.paper });
  paintImage(page, image, { x: 0, y: 0, w: HALF, h: PAGE_H }, "", fonts, ink);
  maskSpread(page, ink);
  const note = book.endNote;
  let y = 520;
  drawRuns(page, note.heading, TEXT_X, y, 28, ink.ink, fonts);
  y -= 20;
  page.drawRectangle({ x: TEXT_X, y, width: 64, height: 1.15, color: GOLD });
  y -= 28;
  for (const paragraph of note.paragraphs) {
    for (const line of wrapWords(paragraph, fonts, 12, TEXT_W)) {
      drawRuns(page, line, TEXT_X, y, 12, ink.ink, fonts);
      y -= 18;
    }
    y -= 8;
  }
  y -= 6;
  for (const line of note.sign) {
    drawRuns(page, line, TEXT_X, y, 12, ink.ink, fonts);
    y -= 18;
  }
  footer(page, fonts, pageNo, "spread", ink);
}

function footer(page: PDFPage, fonts: Fonts, pageNo: number, align: "center" | "spread" = "center", ink: Ink = toneOf("light")) {
  const label = String(pageNo);
  const w = widthOf(label, fonts, 9);
  const x = align === "spread" ? HALF + (HALF - w) / 2 : (PAGE_W - w) / 2;
  drawRuns(page, label, x, 16, 9, ink.muted, fonts);
}

function addLinks(
  pdf: PDFDocument,
  page: PDFPage,
  links: { rect: [number, number, number, number]; page: PDFPage }[],
) {
  const refs = links.map((link) =>
    pdf.context.register(
      pdf.context.obj({
        Type: "Annot",
        Subtype: "Link",
        Rect: link.rect,
        Border: [0, 0, 0],
        Dest: [link.page.ref, "XYZ", null, null, null],
      }),
    ),
  );
  page.node.set(PDFName.of("Annots"), pdf.context.obj(refs));
}

function addOutlines(pdf: PDFDocument, items: { title: string; page: PDFPage }[]) {
  const outlinesRef = pdf.context.nextRef();
  const refs = items.map(() => pdf.context.nextRef());
  items.forEach((item, index) => {
    pdf.context.assign(
      refs[index],
      pdf.context.obj({
        Title: PDFHexString.fromText(item.title),
        Parent: outlinesRef,
        Dest: [item.page.ref, "XYZ", null, null, null],
        ...(index > 0 ? { Prev: refs[index - 1] } : {}),
        ...(index < items.length - 1 ? { Next: refs[index + 1] } : {}),
      }),
    );
  });
  pdf.context.assign(
    outlinesRef,
    pdf.context.obj({
      Type: "Outlines",
      First: refs[0],
      Last: refs[refs.length - 1],
      Count: items.length,
    }),
  );
  pdf.catalog.set(PDFName.of("Outlines"), outlinesRef);
  pdf.catalog.set(PDFName.of("PageMode"), PDFName.of("UseOutlines"));
}
