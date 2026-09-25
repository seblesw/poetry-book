import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { getPoetryBookPdf, type PdfTone } from "../lib/pdf/generate";

async function main() {
  const dir = path.join(process.cwd(), "public", "pdf");
  await mkdir(dir, { recursive: true });

  for (const tone of ["light", "dark"] as const satisfies readonly PdfTone[]) {
    const bytes = await getPoetryBookPdf(tone);
    const name = `Achachir-Gitmoch-Digital-Poetry-Book-${tone}.pdf`;
    await writeFile(path.join(dir, name), bytes);
    console.log(name, bytes.byteLength);
  }
}

main();
