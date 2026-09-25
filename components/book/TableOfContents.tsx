"use client";

import { useEffect, useRef } from "react";
import { poems, type Poem } from "@/lib/poems";
import { IconClose } from "@/components/book/icons";

export function TableOfContents({
  current,
  onClose,
  onSelect,
}: {
  current?: string;
  onClose: () => void;
  onSelect: (slug: string) => void;
}) {
  const closeRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    closeRef.current?.focus();
  }, []);

  return (
    <div className="bk-overlay is-toc" onMouseDown={onClose}>
      <div
        className="bk-dialog is-toc"
        role="dialog"
        aria-modal="true"
        aria-labelledby="toc-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="bk-dialog-head">
          <h2 id="toc-title">ማውጫ</h2>
          <button ref={closeRef} className="bk-btn" type="button" onClick={onClose} aria-label="ማውጫውን ዝጋ">
            <IconClose />
          </button>
        </div>
        <ol className="bk-toc-list">
          <li>
            <button type="button" onClick={() => onSelect("cover")}>
              <span className="bk-num">ሽፋን</span>
              <span>የመጽሐፉ ሽፋን</span>
            </button>
          </li>
          {poems.map((poem: Poem) => (
            <li key={poem.id}>
              <button type="button" aria-current={poem.slug === current ? "true" : undefined} onClick={() => onSelect(poem.slug)}>
                <span className="bk-num">{String(poem.number).padStart(2, "0")}</span>
                <span>{poem.title}</span>
              </button>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
