"use client";

import { book } from "@/content/book";
import { StoryImage } from "@/components/book/StoryImage";
import { DownloadPdf, type PdfStatus } from "@/components/book/DownloadPdf";

export function EndOfBook({
  onReadAgain,
  onContents,
  onShare,
  pdfStatus,
  onDownload,
}: {
  onReadAgain: () => void;
  onContents: () => void;
  onShare: () => void;
  pdfStatus: PdfStatus;
  onDownload: (tone: "light" | "dark") => void;
}) {
  return (
    <div className="bk-book">
      <StoryImage src={book.endImage} alt={book.endAlt} priority />
      <div className="bk-spine" aria-hidden="true" />
      <section className="bk-page bk-end" aria-labelledby="end-title">
        <p className="bk-kicker">{book.series}</p>
        <h2 id="end-title" tabIndex={-1}>
          መጨረሻ
        </h2>
        <hr className="bk-rule" />
        <p>{book.title}</p>
        <p>ሃያ ስምንት ማራኪ የፍቅር ግጥሞች።</p>
        <p>{book.credit}</p>
        <div className="bk-end-actions">
          <button type="button" onClick={onReadAgain}>
            እንደገና አንብብ
          </button>
          <button type="button" onClick={onContents}>
            ማውጫ
          </button>
          <button type="button" onClick={onShare}>
            አጋራ
          </button>
          <DownloadPdf status={pdfStatus} onDownload={onDownload} />
        </div>
      </section>
    </div>
  );
}
