import { book } from "@/content/book";
import { getPoetryBookPdf } from "@/lib/pdf/generate";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const theme = new URL(request.url).searchParams.get("theme") === "dark" ? "dark" : "light";
  const fileName = book.pdfFileName.replace(/\.pdf$/i, theme === "dark" ? "-dark.pdf" : "-light.pdf");
  try {
    const bytes = await getPoetryBookPdf(theme);
    return new Response(Buffer.from(bytes), {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="${fileName}"`,
        "Cache-Control": "private, no-store",
      },
    });
  } catch (error) {
    console.error(error);
    return Response.json({ error: "PDF generation failed" }, { status: 500 });
  }
}
