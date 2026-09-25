"use client";

import { useEffect, useRef } from "react";

export function useSwipe(onPrev: () => void, onNext: () => void) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    let startX = 0;
    let startY = 0;
    let tracking = false;

    const start = (event: TouchEvent) => {
      if (event.touches.length !== 1) return;
      startX = event.touches[0].clientX;
      startY = event.touches[0].clientY;
      tracking = true;
    };
    const end = (event: TouchEvent) => {
      if (!tracking) return;
      tracking = false;
      const touch = event.changedTouches[0];
      const dx = touch.clientX - startX;
      const dy = touch.clientY - startY;
      if (Math.abs(dx) < 64 || Math.abs(dx) < Math.abs(dy) * 1.25) return;
      if (dx < 0) onNext();
      else onPrev();
    };
    const cancel = () => {
      tracking = false;
    };

    node.addEventListener("touchstart", start, { passive: true });
    node.addEventListener("touchend", end, { passive: true });
    node.addEventListener("touchcancel", cancel, { passive: true });
    return () => {
      node.removeEventListener("touchstart", start);
      node.removeEventListener("touchend", end);
      node.removeEventListener("touchcancel", cancel);
    };
  }, [onNext, onPrev]);

  return ref;
}
