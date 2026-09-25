import { book } from "@/content/book";
import { getPoetryBookPdf } from "@/lib/pdf/generate";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const bytes = await getPoetryBookPdf();
    return new Response(Buffer.from(bytes), {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="${book.pdfFileName}"`,
        "Cache-Control": "public, max-age=86400",
      },
    });
  } catch (error) {
    console.error(error);
    return Response.json({ error: "PDF generation failed" }, { status: 500 });
  }
}
