"use client";

import { book } from "@/content/book";
import { IconDownload } from "@/components/book/icons";

export type PdfStatus = "idle" | "preparing" | "ready" | "error";

export function DownloadPdf({
  status,
  onDownload,
}: {
  status: PdfStatus;
  onDownload: () => void;
}) {
  const labels: Record<PdfStatus, string> = {
    idle: "PDF አውርድ",
    preparing: "እየተዘጋጀ ነው",
    ready: "PDF አውርድ",
    error: "እንደገና ሞክር",
  };

  return (
    <button
      className="bk-btn"
      type="button"
      onClick={onDownload}
      disabled={status === "preparing"}
      aria-label={status === "preparing" ? "የግጥም መጽሐፉ እየተዘጋጀ ነው" : "ሙሉውን መጽሐፍ በፒዲኤፍ አውርድ"}
    >
      <IconDownload />
      <span className="bk-btn-label">{labels[status]}</span>
    </button>
  );
}

export async function downloadPoetryPdf(): Promise<void> {
  const response = await fetch("/api/poetry/pdf");
  if (!response.ok) throw new Error("pdf");
  const blob = await response.blob();
  const href = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = href;
  link.download = book.pdfFileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(href);
}
