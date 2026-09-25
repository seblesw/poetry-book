"use client";

import { useEffect, useRef } from "react";
import type { Poem } from "@/lib/poems";
import { PoemText } from "@/components/book/PoemText";

export function PoemPage({ poem }: { poem: Poem }) {
  const titleRef = useRef<HTMLHeadingElement>(null);
  const pageRef = useRef<HTMLElement>(null);

  useEffect(() => {
    titleRef.current?.focus({ preventScroll: true });
  }, [poem.id]);

  const long = poem.text.split("\n").length > 18;

  return (
    <article className="bk-page" ref={pageRef} aria-labelledby={`poem-${poem.id}-title`}>
      <p className="bk-kicker">{String(poem.number).padStart(2, "0")}</p>
      <h1 id={`poem-${poem.id}-title`} className="bk-poem-title" tabIndex={-1} ref={titleRef}>
        {poem.title}
      </h1>
      <hr className="bk-rule" />
      <PoemText text={poem.text} />
      {long ? <p className="bk-scroll-hint">ግጥሙ ከገጹ ረዘም ካለ ያንሸራትቱ።</p> : null}
    </article>
  );
}
