"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";

type Chrome = {
  fullscreen: boolean;
  toggleFullscreen: () => void;
  exitFullscreen: () => void;
};
const BookChromeContext = createContext<Chrome | null>(null);
export function useBookChrome() {
  const value = useContext(BookChromeContext);
  if (!value) throw new Error("Book chrome is missing");
  return value;
}
export function BookChrome({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const [nativeFs, setNativeFs] = useState(false);
  const [immersive, setImmersive] = useState(false);
  useEffect(() => {
    const onChange = () => setNativeFs(document.fullscreenElement === ref.current);
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, []);
  const exitFullscreen = useCallback(async () => {
    setImmersive(false);
    if (document.fullscreenElement) {
      try {
        await document.exitFullscreen();
      } catch {
        setNativeFs(false);
      }
    }
  }, []);

  const toggleFullscreen = useCallback(async () => {
    const node = ref.current;
    if (!node) return;
    if (document.fullscreenElement || immersive) {
      await exitFullscreen();
      return;
    }
    if (typeof node.requestFullscreen === "function") {
      try {
        await node.requestFullscreen();
        return;
      } catch {
        setImmersive(true);
        return;
      }
    }
    setImmersive(true);
  }, [exitFullscreen, immersive]);

  return (
    <BookChromeContext.Provider value={{ fullscreen: nativeFs || immersive, toggleFullscreen, exitFullscreen }}>
      <div ref={ref} className={`bk-root${immersive ? " is-immersive" : ""}${nativeFs ? " is-fullscreen" : ""}`}>
        {children}
      </div>
    </BookChromeContext.Provider>
  );
}
