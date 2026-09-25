"use client";

import { useState } from "react";
import { book } from "@/content/book";
import { IconDownload } from "@/components/book/icons";

export type PdfStatus = "idle" | "preparing" | "ready" | "error";
export type PdfTone = "light" | "dark";

export function DownloadPdf({
  status,
  onDownload,
}: {
  status: PdfStatus;
  onDownload: (tone: PdfTone) => void;
}) {
  const [open, setOpen] = useState(false);
  const labels: Record<PdfStatus, string> = {
    idle: "PDF አውርድ",
    preparing: "እየተዘጋጀ ነው",
    ready: "PDF አውርድ",
    error: "እንደገና ሞክር",
  };

  function choose(tone: PdfTone) {
    setOpen(false);
    onDownload(tone);
  }

  return (
    <div className="bk-pdf">
      {open ? (
        <div className="bk-pdf-menu" role="menu" aria-label="የፒዲኤፍ ገጽ">
          <button type="button" role="menuitem" onClick={() => choose("light")}>
            ብርሃን
          </button>
          <button type="button" role="menuitem" onClick={() => choose("dark")}>
            ጨለማ
          </button>
        </div>
      ) : null}
      <button
        className="bk-btn"
        type="button"
        onClick={() => setOpen((value) => !value)}
        disabled={status === "preparing"}
        aria-expanded={open}
        aria-haspopup="menu"
        aria-label={status === "preparing" ? "የግጥም መጽሐፉ እየተዘጋጀ ነው" : "ሙሉውን መጽሐፍ በፒዲኤፍ አውርድ"}
      >
        <IconDownload />
        <span className="bk-btn-label">{labels[status]}</span>
      </button>
    </div>
  );
}

export function poetryPdfPath(tone: PdfTone) {
  const fileName = book.pdfFileName.replace(/\.pdf$/i, tone === "dark" ? "-dark.pdf" : "-light.pdf");
  return { href: `/pdf/${fileName}`, fileName };
}

export async function downloadPoetryPdf(tone: PdfTone): Promise<void> {
  const { href, fileName } = poetryPdfPath(tone);
  const response = await fetch(href);
  if (!response.ok) throw new Error("pdf");
  const blob = await response.blob();
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
}
