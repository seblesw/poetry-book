"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { book } from "@/content/book";
import { audioFor, END_SLUG, getPoem, neighbors, poemCount } from "@/lib/poems";
import { BookControls } from "@/components/book/BookControls";
import { BookSpread } from "@/components/book/BookSpread";
import { downloadPoetryPdf, type PdfStatus } from "@/components/book/DownloadPdf";
import { EndOfBook } from "@/components/book/EndOfBook";
import { PoemSearch } from "@/components/book/PoemSearch";
import { ProgressIndicator } from "@/components/book/ProgressIndicator";
import { ShareSheet } from "@/components/book/ShareSheet";
import { TableOfContents } from "@/components/book/TableOfContents";
import { useBookChrome } from "@/components/book/BookChrome";
import { useSwipe } from "@/components/book/useSwipe";

const THEME_KEY = "poetry-theme";
const SOUND_KEY = "poetry-sound";

export function PoetryBook({ slug }: { slug: string }) {
  const router = useRouter();
  const chrome = useBookChrome();
  const poem = slug === END_SLUG ? null : getPoem(slug);
  const ended = slug === END_SLUG;
  const adjacent = neighbors(slug);
  const [direction, setDirection] = useState<"next" | "prev">("next");
  const [opening, setOpening] = useState(false);
  const [tocOpen, setTocOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [share, setShare] = useState<{ title: string; url: string } | null>(null);
  const [dark, setDark] = useState(false);
  const [soundOn, setSoundOn] = useState(false);
  const [note, setNote] = useState("");
  const [noteError, setNoteError] = useState(false);
  const [pdfStatus, setPdfStatus] = useState<PdfStatus>("idle");
  const audioRef = useRef<HTMLAudioElement>(null);
  const audioSrc = audioFor(poem);

  useEffect(() => {
    const stored = window.sessionStorage.getItem("poetry-dir");
    if (stored === "prev" || stored === "next") setDirection(stored);
    if (window.sessionStorage.getItem("poetry-open") === "1") {
      window.sessionStorage.removeItem("poetry-open");
      setOpening(true);
      const timer = window.setTimeout(() => setOpening(false), 1200);
      return () => window.clearTimeout(timer);
    }
    return undefined;
  }, [slug]);

  useEffect(() => {
    const theme = document.documentElement.dataset.theme === "dark";
    setDark(theme);
    setSoundOn(window.localStorage.getItem(SOUND_KEY) === "on");
  }, []);

  useEffect(() => {
    const stage = document.querySelector(".bk-stage");
    if (!(stage instanceof HTMLElement)) return;
    if (window.matchMedia("(pointer: coarse)").matches) return;
    let timer = 0;
    const wake = () => {
      stage.classList.remove("is-quiet");
      window.clearTimeout(timer);
      timer = window.setTimeout(() => stage.classList.add("is-quiet"), 2600);
    };
    wake();
    stage.addEventListener("mousemove", wake);
    return () => {
      stage.removeEventListener("mousemove", wake);
      window.clearTimeout(timer);
    };
  }, [slug]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (!audioSrc || !soundOn) {
      fadeOut(audio);
      return;
    }
    if (audio.src !== new URL(audioSrc, window.location.href).href) audio.src = audioSrc;
    audio.volume = 0;
    audio.play().then(() => fadeTo(audio, 0.18)).catch(() => {
      setSoundOn(false);
      window.localStorage.setItem(SOUND_KEY, "off");
    });
  }, [audioSrc, soundOn, slug]);

  const go = useCallback(
    (nextSlug: string | null, dir: "next" | "prev") => {
      if (!nextSlug) return;
      setTocOpen(false);
      setSearchOpen(false);
      setShare(null);
      setDirection(dir);
      window.sessionStorage.setItem("poetry-dir", dir);
      router.push(`/poetry/${nextSlug}`, { scroll: false });
    },
    [router],
  );

  const goPrev = useCallback(() => go(adjacent.prev, "prev"), [adjacent.prev, go]);
  const goNext = useCallback(() => go(adjacent.next, "next"), [adjacent.next, go]);
  const selectPoem = useCallback(
    (nextSlug: string) => {
      const currentNumber = poem?.number ?? poemCount + 1;
      const target = getPoem(nextSlug)?.number ?? currentNumber;
      go(nextSlug, target < currentNumber ? "prev" : "next");
    },
    [go, poem?.number],
  );
  const swipeRef = useSwipe(goPrev, goNext);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target;
      const typing = target instanceof HTMLElement && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable);
      if (event.key === "Escape") {
        if (typing) return;
        if (tocOpen || searchOpen || share) {
          setTocOpen(false);
          setSearchOpen(false);
          setShare(null);
          return;
        }
        void chrome.exitFullscreen();
        return;
      }
      if (typing) return;
      if (tocOpen || searchOpen || share) return;
      if ((target instanceof HTMLButtonElement || target instanceof HTMLAnchorElement) && event.key === " ") return;
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        goPrev();
      } else if (event.key === "ArrowRight" || event.key === " ") {
        event.preventDefault();
        goNext();
      } else if (event.key === "t" || event.key === "T") {
        setTocOpen(true);
      } else if (event.key === "/") {
        event.preventDefault();
        setSearchOpen(true);
      } else if (event.key === "f" || event.key === "F") {
        void chrome.toggleFullscreen();
      } else if (event.key === "m" || event.key === "M") {
        toggleSound();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  function toggleTheme() {
    const next = !dark;
    setDark(next);
    document.documentElement.dataset.theme = next ? "dark" : "light";
    window.localStorage.setItem(THEME_KEY, next ? "dark" : "light");
  }

  function toggleSound() {
    const next = !soundOn;
    setSoundOn(next);
    window.localStorage.setItem(SOUND_KEY, next ? "on" : "off");
    if (!audioSrc) {
      setNoteError(false);
      setNote("ለዚህ መጽሐፍ ድምፅ አልተቀመጠም።");
    }
  }

  async function onShare() {
    const path = ended ? "/poetry/end" : `/poetry/${poem?.slug ?? "1"}`;
    const url = `${window.location.origin}${path}`;
    const text = poem ? `${book.title} — ${poem.title}` : book.title;
    if (typeof navigator.share === "function") {
      try {
        await navigator.share({ title: book.title, text, url });
        return;
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") return;
      }
    }
    setShare({ title: text, url });
  }

  async function onDownload() {
    setPdfStatus("preparing");
    setNoteError(false);
    setNote("መጽሐፉ እየተዘጋጀ ነው…");
    try {
      await downloadPoetryPdf();
      setPdfStatus("ready");
      setNote("የግጥም መጽሐፍዎ ዝግጁ ነው።");
      window.setTimeout(() => setPdfStatus("idle"), 2500);
    } catch {
      setPdfStatus("error");
      setNoteError(true);
      setNote("ፒዲኤፉ አልተዘጋጀም። እንደገና ይሞክሩ።");
    }
  }

  useEffect(() => {
    const nextImage = adjacent.next && adjacent.next !== END_SLUG ? getPoem(adjacent.next)?.image : null;
    const prevImage = adjacent.prev && adjacent.prev !== END_SLUG ? getPoem(adjacent.prev)?.image : null;
    [nextImage, prevImage].forEach((src) => {
      if (!src) return;
      const image = new window.Image();
      image.src = src;
    });
  }, [adjacent.next, adjacent.prev]);

  if (!poem && !ended) return null;

  return (
    <div className={`bk-stage${opening ? " is-opening" : ""}`}>
      <header className="bk-top">
        <Link href="/" className="bk-mark" onClick={() => void chrome.exitFullscreen()}>
          {book.title}
        </Link>
        <ProgressIndicator number={poem?.number} ended={ended} />
      </header>
      <div ref={swipeRef} className={`bk-spread is-${direction}`} key={slug}>
        {ended ? (
          <EndOfBook
            onReadAgain={() => go("1", "next")}
            onContents={() => setTocOpen(true)}
            onShare={() => void onShare()}
            pdfStatus={pdfStatus}
            onDownload={() => void onDownload()}
          />
        ) : poem ? (
          <BookSpread poem={poem} priority />
        ) : null}
      </div>
      <p className="sr-only" aria-live="polite">
        {ended ? "መጨረሻ" : `${poem?.number} ከ ${poemCount}. ${poem?.title}`}
      </p>
      <BookControls
        onPrev={goPrev}
        onNext={goNext}
        canPrev={Boolean(adjacent.prev)}
        canNext={Boolean(adjacent.next)}
        onToc={() => setTocOpen(true)}
        onSearch={() => setSearchOpen(true)}
        onTheme={toggleTheme}
        dark={dark}
        onFullscreen={() => void chrome.toggleFullscreen()}
        fullscreen={chrome.fullscreen}
        soundOn={soundOn}
        hasAudio={Boolean(audioSrc)}
        onSound={toggleSound}
        onShare={() => void onShare()}
        pdfStatus={pdfStatus}
        onDownload={() => void onDownload()}
      />
      <p className={`bk-note${noteError ? " is-error" : ""}`} aria-live="polite">
        {note}
      </p>
      {tocOpen ? (
        <TableOfContents current={poem?.slug} onClose={() => setTocOpen(false)} onSelect={selectPoem} />
      ) : null}
      {searchOpen ? <PoemSearch onClose={() => setSearchOpen(false)} onSelect={selectPoem} /> : null}
      {share ? <ShareSheet title={share.title} url={share.url} onClose={() => setShare(null)} /> : null}
      <audio ref={audioRef} className="sr-only" preload="none" loop />
    </div>
  );
}

function fadeTo(audio: HTMLAudioElement, target: number) {
  audio.volume = 0;
  const step = () => {
    if (!audio.paused && audio.volume < target) {
      audio.volume = Math.min(target, audio.volume + 0.02);
      window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
}

function fadeOut(audio: HTMLAudioElement) {
  const step = () => {
    if (audio.volume > 0.02) {
      audio.volume = Math.max(0, audio.volume - 0.04);
      window.requestAnimationFrame(step);
    } else {
      audio.pause();
      audio.volume = 0;
    }
  };
  if (!audio.paused) window.requestAnimationFrame(step);
}
