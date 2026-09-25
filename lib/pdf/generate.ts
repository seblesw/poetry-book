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

const BODY = 11.25;
const LEAD = 17;
const BLANK = 10;
const TITLE = 20;
const TITLE_LEAD = 26;
const TEXT_X = HALF + 40;
const TEXT_W = HALF - 80;

type Fonts = {
  body: PDFFont;
  emoji: PDFFont;
  bodySet: Set<number>;
  emojiSet: Set<number>;
};

type Run = { text: string; font: PDFFont };

let cached: Promise<Uint8Array> | null = null;

export function getPoetryBookPdf(): Promise<Uint8Array> {
  if (!cached) {
    cached = build().catch((error: unknown) => {
      cached = null;
      throw error;
    });
  }
  return cached;
}

async function build(): Promise<Uint8Array> {
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
  let cursor = 3;
  chunks.forEach((pages, index) => {
    starts.push(cursor - 3);
    poemPdfIndex.set(poems[index].id, cursor);
    cursor += pages.length;
  });
  const total = cursor + 1;

  const cover = pdf.addPage([PAGE_W, PAGE_H]);
  const titlePage = pdf.addPage([PAGE_W, PAGE_H]);
  const tocPage = pdf.addPage([PAGE_W, PAGE_H]);
  const poemPages: PDFPage[] = [];
  chunks.forEach((pages) => {
    pages.forEach(() => poemPages.push(pdf.addPage([PAGE_W, PAGE_H])));
  });
  const endPage = pdf.addPage([PAGE_W, PAGE_H]);

  drawCover(cover, await plate(book.coverImage), fonts);
  drawTitlePage(titlePage, fonts, 2);
  const tocLinks = drawToc(tocPage, fonts, poemPdfIndex, poemPages, starts, 3);
  addLinks(pdf, tocPage, tocLinks);

  let drawn = 0;
  for (let i = 0; i < poems.length; i += 1) {
    const image = await plate(poems[i].image);
    chunks[i].forEach((lines, part) => {
      drawPoemSpread(poemPages[drawn], poems[i], lines, part === 0, image, fonts, poemPdfIndex.get(poems[i].id)! + part + 1);
      drawn += 1;
    });
  }
  drawEnd(endPage, await plate(book.endImage), fonts, total);

  addOutlines(pdf, [
    { title: "ሽፋን", page: cover },
    { title: "ርዕስ", page: titlePage },
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
) {
  let cursor = x;
  for (const run of runsOf(text, fonts)) {
    page.drawText(run.text, { x: cursor, y, size, font: run.font, color });
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
    flat.push(...wrap(raw, fonts, BODY, TEXT_W));
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
  return wrap(title, fonts, TITLE, TEXT_W).length * TITLE_LEAD + 26;
}

function paintImage(page: PDFPage, image: PDFImage | null, box: { x: number; y: number; w: number; h: number }, fallback: string, fonts: Fonts) {
  if (!image) {
    page.drawRectangle({ x: box.x, y: box.y, width: box.w, height: box.h, color: DARK });
    drawRuns(page, fallback, box.x + 28, box.y + box.h / 2, 28, CREAM, fonts);
    return;
  }
  const scale = Math.max(box.w / image.width, box.h / image.height);
  const w = image.width * scale;
  const h = image.height * scale;
  page.drawImage(image, {
    x: box.x + (box.w - w) / 2,
    y: box.y + (box.h - h) / 2,
    width: w,
    height: h,
  });
}

function maskSpread(page: PDFPage) {
  page.drawRectangle({ x: 0, y: 0, width: 18, height: PAGE_H, color: PAPER });
  page.drawRectangle({ x: 0, y: 0, width: HALF, height: 18, color: PAPER });
  page.drawRectangle({ x: 0, y: PAGE_H - 18, width: HALF, height: 18, color: PAPER });
  page.drawRectangle({ x: HALF - 11, y: 0, width: PAGE_W - HALF + 11, height: PAGE_H, color: PAPER });
  page.drawRectangle({ x: HALF - 9, y: 0, width: 18, height: PAGE_H, color: rgb(0.16, 0.09, 0.06) });
  page.drawRectangle({ x: HALF - 0.5, y: 0, width: 1, height: PAGE_H, color: GOLD });
}

function drawCover(page: PDFPage, image: PDFImage | null, fonts: Fonts) {
  page.drawRectangle({ x: 0, y: 0, width: PAGE_W, height: PAGE_H, color: DARK });
  paintImage(page, image, { x: 0, y: 0, w: HALF, h: PAGE_H }, "", fonts);
  page.drawRectangle({ x: HALF - 8, y: 0, width: PAGE_W - HALF + 8, height: PAGE_H, color: DARK });
  page.drawRectangle({ x: HALF - 1, y: 48, width: 1, height: PAGE_H - 96, color: GOLD });

  const x = HALF + 48;
  drawRuns(page, `${book.series}  ·  ${book.issue}`, x, 430, 12, GOLD, fonts);
  let y = 390;
  for (const line of wrap(book.title, fonts, 36, HALF - 96)) {
    drawRuns(page, line, x, y, 36, CREAM, fonts);
    y -= 46;
  }
  drawRuns(page, "ሃያ ስምንት አጫጭር ግጥሞች", x, y - 8, 13, rgb(0.86, 0.78, 0.68), fonts);
  page.drawRectangle({ x, y: 176, width: 64, height: 1.25, color: GOLD });
  let creditY = 150;
  for (const line of wrap(book.credit, fonts, 12, HALF - 96)) {
    drawRuns(page, line, x, creditY, 12, rgb(0.9, 0.84, 0.74), fonts);
    creditY -= 18;
  }
  drawRuns(page, "ዲጂታል የግጥም መጽሐፍ", x, 88, 11, GOLD, fonts);
}

function drawTitlePage(page: PDFPage, fonts: Fonts, pageNo: number) {
  page.drawRectangle({ x: 0, y: 0, width: PAGE_W, height: PAGE_H, color: PAPER });
  page.drawRectangle({ x: 36, y: 36, width: PAGE_W - 72, height: PAGE_H - 72, borderColor: GOLD, borderWidth: 0.8 });
  const title = wrap(book.title, fonts, 34, 520);
  let y = 360;
  for (const line of title) {
    const w = widthOf(line, fonts, 34);
    drawRuns(page, line, (PAGE_W - w) / 2, y, 34, INK, fonts);
    y -= 44;
  }
  const series = `${book.series}  ·  ${book.issue}`;
  drawRuns(page, series, (PAGE_W - widthOf(series, fonts, 13)) / 2, y - 6, 13, MUTED, fonts);
  const creditLines = wrap(book.credit, fonts, 13, 560);
  let creditY = y - 48;
  for (const line of creditLines) {
    drawRuns(page, line, (PAGE_W - widthOf(line, fonts, 13)) / 2, creditY, 13, INK, fonts);
    creditY -= 22;
  }
  const sub = "ሃያ ስምንት አጫጭር ግጥሞች";
  drawRuns(page, sub, (PAGE_W - widthOf(sub, fonts, 12)) / 2, 150, 12, MUTED, fonts);
  footer(page, fonts, pageNo);
}

function drawToc(
  page: PDFPage,
  fonts: Fonts,
  poemPdfIndex: Map<string, number>,
  poemPages: PDFPage[],
  starts: number[],
  pageNo: number,
) {
  page.drawRectangle({ x: 0, y: 0, width: PAGE_W, height: PAGE_H, color: PAPER });
  drawRuns(page, "ማውጫ", 48, PAGE_H - 58, 22, INK, fonts);
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
    drawRuns(page, title, x + 36, y, 12, INK, fonts);
    const destLabel = String(poemPdfIndex.get(poem.id)! + 1);
    drawRuns(page, destLabel, x + 320, y, 10, MUTED, fonts);
    links.push({ rect: [x, y - 6, x + 350, y + 16], page: poemPages[starts[index]] });
  });
  footer(page, fonts, pageNo);
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
) {
  page.drawRectangle({ x: 0, y: 0, width: PAGE_W, height: PAGE_H, color: PAPER });
  paintImage(page, image, { x: 0, y: 0, w: HALF, h: PAGE_H }, String(poem.number).padStart(2, "0"), fonts);
  maskSpread(page);

  let y = PAGE_H - 50;
  if (first) {
    for (const line of wrap(poem.title, fonts, TITLE, TEXT_W)) {
      drawRuns(page, line, TEXT_X, y, TITLE, INK, fonts);
      y -= TITLE_LEAD;
    }
    y -= 6;
    page.drawRectangle({ x: TEXT_X, y: y + 12, width: 64, height: 1.15, color: GOLD });
    y -= 20;
  } else {
    drawRuns(page, fit(poem.title, fonts, 11, TEXT_W - 70), TEXT_X, y, 11, MUTED, fonts);
    drawRuns(page, "ቀጣይ", PAGE_W - 78, y, 10, GOLD, fonts);
    y -= 36;
  }

  for (const line of lines) {
    if (!line) {
      y -= BLANK;
      continue;
    }
    drawRuns(page, line, TEXT_X, y, BODY, INK, fonts);
    y -= LEAD;
  }

  const mark = String(poem.number).padStart(2, "0");
  drawRuns(page, mark, PAGE_W - 58, 32, 11, MUTED, fonts);
  footer(page, fonts, pageNo, "spread");
}

function drawEnd(page: PDFPage, image: PDFImage | null, fonts: Fonts, pageNo: number) {
  page.drawRectangle({ x: 0, y: 0, width: PAGE_W, height: PAGE_H, color: PAPER });
  paintImage(page, image, { x: 0, y: 0, w: HALF, h: PAGE_H }, "", fonts);
  maskSpread(page);
  drawRuns(page, "መጨረሻ", TEXT_X, 360, 32, INK, fonts);
  page.drawRectangle({ x: TEXT_X, y: 336, width: 64, height: 1.15, color: GOLD });
  drawRuns(page, book.title, TEXT_X, 300, 16, INK, fonts);
  drawRuns(page, book.series, TEXT_X, 274, 12, MUTED, fonts);
  drawRuns(page, "ሃያ ስምንት ግጥሞች", TEXT_X, 248, 12, MUTED, fonts);
  footer(page, fonts, pageNo, "spread");
}

function footer(page: PDFPage, fonts: Fonts, pageNo: number, align: "center" | "spread" = "center") {
  const label = String(pageNo);
  const w = widthOf(label, fonts, 9);
  const x = align === "spread" ? HALF + (HALF - w) / 2 : (PAGE_W - w) / 2;
  drawRuns(page, label, x, 16, 9, MUTED, fonts);
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
