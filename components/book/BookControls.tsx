"use client";

import {
  IconExpand,
  IconList,
  IconMoon,
  IconSearch,
  IconShare,
  IconSound,
  IconSun,
} from "@/components/book/icons";
import { DownloadPdf, type PdfStatus } from "@/components/book/DownloadPdf";
import { tracks, type Track } from "@/content/music";

export function BookControls({
  onToc,
  onSearch,
  onTheme,
  dark,
  onFullscreen,
  fullscreen,
  soundOn,
  paused,
  volume,
  trackId,
  onSound,
  onPause,
  onVolume,
  onTrack,
  onShare,
  pdfStatus,
  onDownload,
}: {
  onToc: () => void;
  onSearch: () => void;
  onTheme: () => void;
  dark: boolean;
  onFullscreen: () => void;
  fullscreen: boolean;
  soundOn: boolean;
  paused: boolean;
  volume: number;
  trackId: string;
  onSound: () => void;
  onPause: () => void;
  onVolume: (level: number) => void;
  onTrack: (id: string) => void;
  onShare: () => void;
  pdfStatus: PdfStatus;
  onDownload: () => void;
}) {
  return (
    <div className="bk-dock">
      {soundOn ? (
        <div className="bk-tracks" role="listbox" aria-label="የሙዚቃ ምርጫ">
          {tracks.map((track: Track) => (
            <button
              key={track.id}
              type="button"
              role="option"
              aria-selected={track.id === trackId}
              className={track.id === trackId ? "is-on" : ""}
              onClick={() => onTrack(track.id)}
            >
              <span>{track.title}</span>
              <span className="bk-track-by">{track.composer}</span>
            </button>
          ))}
        </div>
      ) : null}
      {soundOn ? (
        <div className="bk-mix">
          <button type="button" onClick={onPause} aria-pressed={!paused} aria-label={paused ? "ቀጥል" : "አቁም"}>
            {paused ? "ቀጥል" : "አቁም"}
          </button>
          <label className="bk-volume">
            <span>ድምፅ መጠን</span>
            <input
              type="range"
              min={0}
              max={100}
              value={Math.round(volume * 100)}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={Math.round(volume * 100)}
              onChange={(event) => onVolume(Number(event.target.value) / 100)}
            />
          </label>
        </div>
      ) : null}
      <div className="bk-controls" role="toolbar" aria-label="የንባብ መቆጣጠሪያ">
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
        aria-pressed={soundOn}
        aria-keyshortcuts="M"
        aria-label={soundOn ? "ድምፅ አጥፋ" : "ድምፅ አብራ"}
      >
        <IconSound off={!soundOn} />
        <span className="bk-btn-label">ድምፅ</span>
      </button>
      <button className="bk-btn" type="button" onClick={onShare} aria-label="አጋራ">
        <IconShare />
        <span className="bk-btn-label">አጋራ</span>
      </button>
      <DownloadPdf status={pdfStatus} onDownload={onDownload} />
      </div>
    </div>
  );
}
