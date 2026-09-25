"use client";

import {
  IconExpand,
  IconList,
  IconMoon,
  IconNext,
  IconPrev,
  IconSearch,
  IconShare,
  IconSound,
  IconSun,
} from "@/components/book/icons";
import { DownloadPdf, type PdfStatus } from "@/components/book/DownloadPdf";

export function BookControls({
  onPrev,
  onNext,
  canPrev,
  canNext,
  onToc,
  onSearch,
  onTheme,
  dark,
  onFullscreen,
  fullscreen,
  soundOn,
  hasAudio,
  onSound,
  onShare,
  pdfStatus,
  onDownload,
}: {
  onPrev: () => void;
  onNext: () => void;
  canPrev: boolean;
  canNext: boolean;
  onToc: () => void;
  onSearch: () => void;
  onTheme: () => void;
  dark: boolean;
  onFullscreen: () => void;
  fullscreen: boolean;
  soundOn: boolean;
  hasAudio: boolean;
  onSound: () => void;
  onShare: () => void;
  pdfStatus: PdfStatus;
  onDownload: () => void;
}) {
  return (
    <div className="bk-controls" role="toolbar" aria-label="የንባብ መቆጣጠሪያ">
      <button className="bk-btn" type="button" onClick={onPrev} disabled={!canPrev} aria-keyshortcuts="ArrowLeft" aria-label="ቀዳሚ ግጥም">
        <IconPrev />
        <span className="bk-btn-label">ቀዳሚ</span>
      </button>
      <button className="bk-btn" type="button" onClick={onNext} disabled={!canNext} aria-keyshortcuts="ArrowRight" aria-label="ቀጣይ ግጥም">
        <IconNext />
        <span className="bk-btn-label">ቀጣይ</span>
      </button>
      <button className="bk-btn" type="button" onClick={onToc} aria-keyshortcuts="T" aria-label="ማውጫ">
        <IconList />
        <span className="bk-btn-label">ማውጫ</span>
      </button>
      <button className="bk-btn" type="button" onClick={onSearch} aria-keyshortcuts="/" aria-label="ፈልግ">
        <IconSearch />
        <span className="bk-btn-label">ፈልግ</span>
      </button>
      <button className="bk-btn" type="button" onClick={onTheme} aria-pressed={dark} aria-label={dark ? "የብርሃን ገጽ" : "የጨለማ ገጽ"}>
        {dark ? <IconSun /> : <IconMoon />}
        <span className="bk-btn-label">{dark ? "ብርሃን" : "ጨለማ"}</span>
      </button>
      <button className="bk-btn" type="button" onClick={onFullscreen} aria-pressed={fullscreen} aria-keyshortcuts="F" aria-label={fullscreen ? "ከሙሉ ማያ ውጣ" : "ሙሉ ማያ"}>
        <IconExpand />
        <span className="bk-btn-label">ሙሉ ማያ</span>
      </button>
      <button
        className="bk-btn"
        type="button"
        onClick={onSound}
        aria-pressed={hasAudio ? soundOn : undefined}
        aria-disabled={hasAudio ? undefined : true}
        aria-keyshortcuts="M"
        aria-label={hasAudio ? (soundOn ? "ድምፅ አጥፋ" : "ድምፅ አብራ") : "ለዚህ መጽሐፍ ድምፅ አልተቀመጠም"}
      >
        <IconSound />
        <span className="bk-btn-label">ድምፅ</span>
      </button>
      <button className="bk-btn" type="button" onClick={onShare} aria-label="አጋራ">
        <IconShare />
        <span className="bk-btn-label">አጋራ</span>
      </button>
      <DownloadPdf status={pdfStatus} onDownload={onDownload} />
    </div>
  );
}
